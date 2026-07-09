"""聊天服务 - 业务逻辑层"""
import json
import uuid
import logging
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.exceptions import PermissionDeniedError, NotFoundError
from app.models.knowledge_base import KnowledgeBase
from app.models.conversation import Conversation, Message
from app.schemas.chat import ChatRequest, ConversationCreate, ConversationResponse
from app.services.chat import rag_chat
from app.utils.helpers import get_or_404
from app.core.database import async_session

logger = logging.getLogger(__name__)


class ChatService:
    """聊天业务逻辑"""

    @staticmethod
    async def list_conversations(db: AsyncSession, user_id: str) -> list[Conversation]:
        """获取用户的所有对话"""
        result = await db.execute(
            select(Conversation)
            .where(Conversation.user_id == user_id)
            .order_by(Conversation.updated_at.desc())
        )
        return result.scalars().all()

    @staticmethod
    async def create_conversation(
        db: AsyncSession, data: ConversationCreate, user_id: str
    ) -> Conversation:
        """创建对话"""
        # 验证知识库是否存在
        kb_result = await db.execute(
            select(KnowledgeBase).where(KnowledgeBase.id == data.knowledge_base_id)
        )
        kb = kb_result.scalar_one_or_none()
        if not kb:
            raise NotFoundError("知识库", data.knowledge_base_id)

        conv = Conversation(
            user_id=user_id,
            knowledge_base_id=data.knowledge_base_id,
            title=data.title or "新对话",
        )
        db.add(conv)
        await db.commit()
        await db.refresh(conv)
        return conv

    @staticmethod
    async def list_messages(db: AsyncSession, conv_id: str, user_id: str) -> list[Message]:
        """获取对话消息"""
        # 验证对话存在且属于当前用户
        conv = await get_or_404(db, Conversation, conv_id, "对话")
        if conv.user_id != user_id:
            raise PermissionDeniedError("无权访问此对话")

        result = await db.execute(
            select(Message)
            .where(Message.conversation_id == conv_id)
            .order_by(Message.created_at)
        )
        return result.scalars().all()

    @staticmethod
    async def delete_conversation(db: AsyncSession, conv_id: str, user_id: str) -> None:
        """删除对话"""
        conv = await get_or_404(db, Conversation, conv_id, "对话")
        if conv.user_id != user_id:
            raise PermissionDeniedError("无权删除此对话")
        await db.delete(conv)
        await db.commit()

    @staticmethod
    async def chat_stream(data: ChatRequest, db: AsyncSession, user_id: str):
        """流式聊天 SSE 生成器

        注意：由于 StreamingResponse 在 endpoint 返回后才消费生成器，
        此时 FastAPI 已关闭注入的 db session，所以所有 DB 操作必须使用新 session。
        """
        # 所有 DB 操作使用独立 session，避免依赖注入的 session 被提前关闭
        conv_id = data.conversation_id
        conv_title = None
        conv_user_id = None

        async with async_session() as session:
            # 创建或获取对话
            if conv_id:
                conv = await get_or_404(session, Conversation, conv_id, "对话")
                if conv.user_id != user_id:
                    raise PermissionDeniedError("无权访问此对话")
                conv_title = conv.title
                conv_user_id = conv.user_id
            else:
                # 验证知识库是否存在
                kb_result = await session.execute(
                    select(KnowledgeBase).where(KnowledgeBase.id == data.knowledge_base_id)
                )
                kb = kb_result.scalar_one_or_none()
                if not kb:
                    raise NotFoundError("知识库", data.knowledge_base_id)

                conv = Conversation(
                    user_id=user_id,
                    knowledge_base_id=data.knowledge_base_id,
                    title=data.message[:50],
                )
                session.add(conv)
                await session.commit()
                await session.refresh(conv)
                conv_id = conv.id
                conv_title = conv.title
                conv_user_id = conv.user_id

            # 保存用户消息
            user_msg = Message(
                conversation_id=conv_id,
                role="user",
                content=data.message,
            )
            session.add(user_msg)
            await session.commit()

            # 加载对话历史（用于多轮对话记忆）- 排除刚保存的用户消息避免重复
            history_result = await session.execute(
                select(Message)
                .where(Message.conversation_id == conv_id)
                .order_by(Message.created_at)
                .limit(21)  # 多加载1条，后面排除最新的
            )
            history_messages = history_result.scalars().all()
            # 排除最后一条（刚保存的用户消息），避免与 data.message 重复
            if history_messages and history_messages[-1].role == "user":
                history_messages = history_messages[:-1]
            history = [{"role": msg.role, "content": msg.content} for msg in history_messages]

        # 使用固定的消息 ID，保持前端和数据库一致
        message_id = str(uuid.uuid4())

        # 发送开始事件
        yield f"data: {json.dumps({'type': 'start', 'conversation_id': conv_id, 'message_id': message_id})}\n\n"

        # RAG 问答（带对话历史）
        full_response = ""
        all_sources = []
        rag_error = False
        try:
            async for chunk, sources in rag_chat(data.knowledge_base_id, data.message, history):
                full_response += chunk
                all_sources = sources
                yield f"data: {json.dumps({'type': 'chunk', 'content': chunk})}\n\n"
        except Exception as e:
            logger.error(f"RAG 问答失败: {e}")
            error_msg = "抱歉，处理您的问题时出现错误，请稍后重试"
            full_response = error_msg
            rag_error = True
            yield f"data: {json.dumps({'type': 'chunk', 'content': error_msg})}\n\n"

        # 发送来源引用
        if all_sources:
            yield f"data: {json.dumps({'type': 'sources', 'documents': all_sources})}\n\n"

        # 使用新的 session 保存助手消息（仅在 RAG 成功时保存）
        if not rag_error:
            async with async_session() as save_session:
                try:
                    assistant_msg = Message(
                        id=message_id,
                        conversation_id=conv_id,
                        role="assistant",
                        content=full_response,
                        sources=all_sources if all_sources else None,
                    )
                    save_session.add(assistant_msg)

                    # 更新对话标题
                    title_to_check = data.message[:50]
                    if conv_title == "新对话" or conv_title == title_to_check:
                        conv_result = await save_session.execute(
                            select(Conversation).where(Conversation.id == conv_id)
                        )
                        conv_in_session = conv_result.scalar_one()
                        conv_in_session.title = data.message[:100]

                    await save_session.commit()
                except Exception as e:
                    await save_session.rollback()
                    logger.error(f"保存消息失败: {e}")

        # 发送结束事件
        yield f"data: {json.dumps({'type': 'end', 'message_id': message_id})}\n\n"

    @staticmethod
    async def chat_non_stream(data: ChatRequest, db: AsyncSession, user_id: str) -> dict:
        """非流式聊天"""
        # 创建或获取对话
        if data.conversation_id:
            conv = await get_or_404(db, Conversation, data.conversation_id, "对话")
            if conv.user_id != user_id:
                raise PermissionDeniedError("无权访问此对话")
        else:
            # 验证知识库是否存在
            kb_result = await db.execute(
                select(KnowledgeBase).where(KnowledgeBase.id == data.knowledge_base_id)
            )
            kb = kb_result.scalar_one_or_none()
            if not kb:
                raise NotFoundError("知识库", data.knowledge_base_id)

            conv = Conversation(
                user_id=user_id,
                knowledge_base_id=data.knowledge_base_id,
                title=data.message[:50],
            )
            db.add(conv)
            await db.commit()
            await db.refresh(conv)

        # 保存用户消息
        user_msg = Message(
            conversation_id=conv.id,
            role="user",
            content=data.message,
        )
        db.add(user_msg)
        await db.commit()

        # 加载对话历史（用于多轮对话记忆）- 使用新的 session 避免过期
        async with async_session() as history_session:
            history_result = await history_session.execute(
                select(Message)
                .where(Message.conversation_id == conv.id)
                .order_by(Message.created_at)
                .limit(21)  # 多加载1条，后面排除最新的
            )
            history_messages = history_result.scalars().all()
            # 排除最后一条（刚保存的用户消息），避免与 data.message 重复
            if history_messages and history_messages[-1].role == "user":
                history_messages = history_messages[:-1]
            history = [{"role": msg.role, "content": msg.content} for msg in history_messages]

        # RAG 问答（带对话历史）
        full_response = ""
        all_sources = []
        rag_error = False
        try:
            async for chunk, sources in rag_chat(data.knowledge_base_id, data.message, history):
                full_response += chunk
                all_sources = sources
        except Exception as e:
            logger.error(f"RAG 问答失败: {e}")
            full_response = "抱歉，处理您的问题时出现错误，请稍后重试"
            rag_error = True

        # 仅在 RAG 成功时保存助手消息
        message_id = str(uuid.uuid4())
        if not rag_error:
            assistant_msg = Message(
                id=message_id,
                conversation_id=conv.id,
                role="assistant",
                content=full_response,
                sources=all_sources if all_sources else None,
            )
            db.add(assistant_msg)

            # 更新对话标题
            if conv.title in ("新对话", data.message[:50]):
                conv.title = data.message[:100]

            await db.commit()

        return {
            "conversation_id": conv.id,
            "message_id": message_id,
            "content": full_response,
            "sources": all_sources if not rag_error else [],
        }

"""聊天 API"""
import re
import logging
import datetime
from urllib.parse import quote
from typing import Literal
from fastapi import APIRouter, Depends, Query
from fastapi.responses import StreamingResponse, Response
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, or_

from app.core.database import get_db
from app.deps import get_current_user
from app.exceptions import PermissionDeniedError
from app.models.user import User
from app.models.conversation import Conversation, Message
from app.schemas.chat import ChatRequest, ConversationCreate, ConversationResponse, MessageResponse
from app.services.chat_service import ChatService
from app.utils.helpers import get_or_404

logger = logging.getLogger(__name__)
router = APIRouter()


@router.get("/conversations/search", summary="搜索对话")
async def search_conversations(
    q: str = Query(..., min_length=1, description="搜索关键词"),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """搜索对话标题或消息内容"""
    # 搜索标题匹配的对话
    title_result = await db.execute(
        select(Conversation)
        .where(
            Conversation.user_id == current_user.id,
            Conversation.title.contains(q),
        )
        .order_by(Conversation.updated_at.desc())
        .limit(20)
    )
    title_matches = {c.id: c for c in title_result.scalars().all()}

    # 搜索消息内容匹配的对话
    msg_result = await db.execute(
        select(Message.conversation_id)
        .join(Conversation, Message.conversation_id == Conversation.id)
        .where(
            Conversation.user_id == current_user.id,
            Message.content.contains(q),
        )
        .distinct()
        .limit(20)
    )
    msg_conv_ids = [row[0] for row in msg_result.all()]

    # 加载消息匹配的对话
    all_conv_ids = set(title_matches.keys()) | set(msg_conv_ids)
    if not all_conv_ids:
        return {"results": [], "total": 0}

    conv_result = await db.execute(
        select(Conversation)
        .where(Conversation.id.in_(all_conv_ids))
        .order_by(Conversation.updated_at.desc())
    )
    conversations = conv_result.scalars().all()

    return {
        "results": [
            {"id": c.id, "title": c.title, "knowledge_base_id": c.knowledge_base_id, "updated_at": str(c.updated_at)}
            for c in conversations
        ],
        "total": len(conversations),
    }


@router.get("/conversations", response_model=list[ConversationResponse], summary="获取对话列表")
async def list_conversations(
    page: int = Query(1, ge=1, description="页码"),
    page_size: int = Query(20, ge=1, le=100, description="每页数量"),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """获取当前用户的对话列表"""
    items, total = await ChatService.list_conversations(db, current_user.id, page, page_size)
    return items


@router.post(
    "/conversations",
    response_model=ConversationResponse,
    status_code=201,
    summary="创建对话",
)
async def create_conversation(
    data: ConversationCreate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """创建新对话"""
    conv = await ChatService.create_conversation(db, data, current_user.id)
    logger.info(f"创建对话: {conv.id}")
    return conv


@router.get(
    "/conversations/{conv_id}/messages",
    response_model=list[MessageResponse],
    summary="获取消息历史",
)
async def list_messages(
    conv_id: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """获取对话的消息历史"""
    return await ChatService.list_messages(db, conv_id, current_user.id)


@router.delete("/conversations/{conv_id}", status_code=204, summary="删除对话")
async def delete_conversation(
    conv_id: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """删除对话及其所有消息"""
    await ChatService.delete_conversation(db, conv_id, current_user.id)
    logger.info(f"删除对话: {conv_id}")


@router.get("/conversations/{conv_id}/export", summary="导出对话")
async def export_conversation(
    conv_id: str,
    export_format: Literal["markdown", "txt"] = "markdown",
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """导出对话为 Markdown 或 TXT 格式"""
    # 验证对话存在且属于当前用户
    conv = await get_or_404(db, Conversation, conv_id, "对话")
    if conv.user_id != current_user.id:
        raise PermissionDeniedError("无权导出此对话")

    # 获取所有消息
    result = await db.execute(
        select(Message)
        .where(Message.conversation_id == conv_id)
        .order_by(Message.created_at)
    )
    messages = result.scalars().all()

    # 生成内容
    if export_format == "markdown":
        content = generate_markdown(conv.title, messages)
        media_type = "text/markdown"
        ext = "md"
    else:
        content = generate_text(conv.title, messages)
        media_type = "text/plain"
        ext = "txt"

    # 清理文件名中的特殊字符
    safe_title = re.sub(r'[^\w\s-]', '', conv.title).strip()
    if not safe_title:
        safe_title = "conversation"

    # URL 编码文件名以支持中文
    encoded_title = quote(safe_title)

    return Response(
        content=content,
        media_type=media_type,
        headers={
            "Content-Disposition": f"attachment; filename*=UTF-8''{encoded_title}.{ext}"
        }
    )


def generate_markdown(title: str, messages: list) -> str:
    """生成 Markdown 格式的对话内容"""
    lines = [
        f"# {title}",
        "",
        f"导出时间: {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
        "",
        "---",
        "",
    ]

    for msg in messages:
        role = "**用户**" if msg.role == "user" else "**助手**"
        lines.append(f"### {role}")
        lines.append("")
        lines.append(msg.content)
        lines.append("")

        # 添加来源引用
        if msg.sources and isinstance(msg.sources, list) and len(msg.sources) > 0:
            lines.append("**参考来源:**")
            for i, source in enumerate(msg.sources):
                if isinstance(source, dict):
                    source_content = source.get("content", "")[:100]
                    lines.append(f"{i+1}. {source_content}...")
            lines.append("")

        lines.append("---")
        lines.append("")

    return "\n".join(lines)


def generate_text(title: str, messages: list) -> str:
    """生成纯文本格式的对话内容"""
    lines = [
        title,
        "=" * len(title),
        "",
        f"导出时间: {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
        "",
        "-" * 40,
        "",
    ]

    for msg in messages:
        role = "用户" if msg.role == "user" else "助手"
        lines.append(f"[{role}]")
        lines.append(msg.content)
        lines.append("")
        lines.append("-" * 40)
        lines.append("")

    return "\n".join(lines)


@router.post("/chat", summary="发送消息")
async def chat(
    data: ChatRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """发送消息并获取 AI 回答"""
    if data.stream:
        return StreamingResponse(
            ChatService.chat_stream(data, db, current_user.id),
            media_type="text/event-stream",
            headers={
                "Cache-Control": "no-cache",
                "Connection": "keep-alive",
                "X-Accel-Buffering": "no",
            },
        )
    else:
        return await ChatService.chat_non_stream(data, db, current_user.id)

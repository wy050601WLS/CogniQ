"""文档服务"""
import os
import uuid
import asyncio
import logging
from fastapi import UploadFile

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.config import settings
from app.models.document import Document
from app.models.knowledge_base import KnowledgeBase
from app.utils.helpers import get_or_404
from app.exceptions import ValidationError, ProcessingError, PermissionDeniedError

logger = logging.getLogger(__name__)

# 支持的文件类型
SUPPORTED_FILE_TYPES = {"pdf", "docx", "doc", "md", "txt", "html", "htm"}


class DocumentService:
    """文档业务逻辑"""

    @staticmethod
    async def list_by_kb(db: AsyncSession, kb_id: str, user_id: str = None) -> list[Document]:
        """获取知识库下的所有文档"""
        # 如果提供了 user_id，验证知识库所有权
        if user_id:
            kb = await get_or_404(db, KnowledgeBase, kb_id, "知识库")
            if kb.owner_id != user_id:
                raise PermissionDeniedError("无权访问此知识库")

        result = await db.execute(
            select(Document)
            .where(Document.knowledge_base_id == kb_id)
            .order_by(Document.created_at.desc())
        )
        return result.scalars().all()

    @staticmethod
    async def get_by_id(db: AsyncSession, doc_id: str, user_id: str = None) -> Document:
        """获取文档详情"""
        doc = await get_or_404(db, Document, doc_id, "文档")

        # 如果提供了 user_id，验证知识库所有权
        if user_id:
            kb = await get_or_404(db, KnowledgeBase, doc.knowledge_base_id, "知识库")
            if kb.owner_id != user_id:
                raise PermissionDeniedError("无权访问此文档")

        return doc

    @staticmethod
    async def upload_and_process(
        db: AsyncSession, kb_id: str, file: UploadFile, user_id: str = None
    ) -> Document:
        """上传并处理文档"""
        # 验证文件
        if not file.filename:
            raise ValidationError("文件名不能为空")

        # 验证文件类型
        file_ext = file.filename.rsplit(".", 1)[-1].lower() if "." in file.filename else ""
        if file_ext not in SUPPORTED_FILE_TYPES:
            raise ValidationError(
                f"不支持的文件类型: {file_ext}。支持的类型: {', '.join(sorted(SUPPORTED_FILE_TYPES))}"
            )

        # 检查文件大小
        content = await file.read()
        max_size = settings.MAX_UPLOAD_SIZE_MB * 1024 * 1024
        if len(content) > max_size:
            raise ValidationError(f"文件大小超过限制（最大 {settings.MAX_UPLOAD_SIZE_MB}MB）")

        # 获取知识库的分块设置并验证所有权
        kb_result = await db.execute(
            select(KnowledgeBase).where(KnowledgeBase.id == kb_id)
        )
        kb = kb_result.scalar_one_or_none()
        if not kb:
            raise ValidationError("知识库不存在")

        # 验证用户是否有权上传到此知识库
        if user_id and kb.owner_id != user_id:
            raise PermissionDeniedError("无权上传文档到此知识库")

        # 保存文件
        file_name = f"{uuid.uuid4()}.{file_ext}"
        file_path = os.path.join(settings.UPLOAD_DIR, file_name)

        os.makedirs(settings.UPLOAD_DIR, exist_ok=True)
        try:
            with open(file_path, "wb") as f:
                f.write(content)
        except Exception as e:
            logger.error(f"文件保存失败: {e}")
            raise ProcessingError("文件保存失败")

        # 创建文档记录
        doc = Document(
            knowledge_base_id=kb_id,
            filename=file.filename,
            file_type=file_ext,
            file_size=len(content),
            file_path=file_path,
            status="processing",
        )
        db.add(doc)
        await db.commit()
        await db.refresh(doc)

        # 处理文档（使用知识库的分块设置，线程池避免阻塞事件循环）
        try:
            from app.services.chat import process_document

            chunk_count = await asyncio.to_thread(
                process_document,
                kb_id=kb_id,
                doc_id=doc.id,
                file_path=file_path,
                chunk_size=kb.chunk_size,
                chunk_overlap=kb.chunk_overlap,
            )
            doc.status = "completed"
            doc.chunk_count = chunk_count
            logger.info(f"文档处理完成: {file.filename}, 分块数: {chunk_count}")
        except Exception as e:
            doc.status = "error"
            doc.error_message = str(e)[:500]  # 限制错误信息长度
            logger.error(f"文档处理失败: {e}")

        await db.commit()
        await db.refresh(doc)
        return doc

    @staticmethod
    async def delete(db: AsyncSession, doc_id: str, user_id: str = None) -> None:
        """删除文档"""
        doc = await get_or_404(db, Document, doc_id, "文档")

        # 验证用户是否有权删除此文档
        if user_id:
            kb = await get_or_404(db, KnowledgeBase, doc.knowledge_base_id, "知识库")
            if kb.owner_id != user_id:
                raise PermissionDeniedError("无权删除此文档")

        # 删除向量数据
        try:
            from app.services.vector_store import get_vector_store
            vector_store = get_vector_store()
            vector_store.delete_documents(doc.knowledge_base_id, [doc.id])
        except Exception as e:
            logger.warning(f"删除向量数据失败: {e}")

        # 删除磁盘上的文件
        if doc.file_path:
            try:
                if os.path.exists(doc.file_path):
                    os.remove(doc.file_path)
                    logger.info(f"已删除磁盘文件: {doc.file_path}")
            except Exception as e:
                logger.warning(f"删除磁盘文件失败: {e}")

        await db.delete(doc)
        await db.commit()

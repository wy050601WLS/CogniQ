"""知识库服务"""
import os
import logging
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.config import settings
from app.models.knowledge_base import KnowledgeBase
from app.models.user import User
from app.models.document import Document
from app.schemas.knowledge_base import KnowledgeBaseCreate, KnowledgeBaseUpdate
from app.utils.helpers import get_or_404
from app.exceptions import PermissionDeniedError

logger = logging.getLogger(__name__)


class KnowledgeBaseService:
    """知识库业务逻辑"""

    @staticmethod
    async def list_by_owner(db: AsyncSession, owner_id: str, page: int = 1, page_size: int = 20) -> tuple[list[KnowledgeBase], int]:
        """获取用户的知识库（分页）"""
        # 获取总数
        from sqlalchemy import func
        count_result = await db.execute(
            select(func.count(KnowledgeBase.id)).where(KnowledgeBase.owner_id == owner_id)
        )
        total = count_result.scalar() or 0

        # 获取分页数据
        offset = (page - 1) * page_size
        result = await db.execute(
            select(KnowledgeBase)
            .where(KnowledgeBase.owner_id == owner_id)
            .order_by(KnowledgeBase.created_at.desc())
            .offset(offset)
            .limit(page_size)
        )
        return result.scalars().all(), total

    @staticmethod
    async def list_public(db: AsyncSession, page: int = 1, page_size: int = 20) -> tuple[list[KnowledgeBase], int]:
        """获取公开知识库（广场），排除禁用用户的知识库（分页）"""
        # 获取总数
        from sqlalchemy import func
        count_result = await db.execute(
            select(func.count(KnowledgeBase.id))
            .join(User, KnowledgeBase.owner_id == User.id)
            .where(
                ((KnowledgeBase.is_public == True) | (KnowledgeBase.is_official == True))
                & (User.status == "active")
            )
        )
        total = count_result.scalar() or 0

        # 获取分页数据
        offset = (page - 1) * page_size
        result = await db.execute(
            select(KnowledgeBase)
            .join(User, KnowledgeBase.owner_id == User.id)
            .where(
                ((KnowledgeBase.is_public == True) | (KnowledgeBase.is_official == True))
                & (User.status == "active")
            )
            .order_by(KnowledgeBase.created_at.desc())
            .offset(offset)
            .limit(page_size)
        )
        return result.scalars().all(), total

    @staticmethod
    async def create(db: AsyncSession, data: KnowledgeBaseCreate, user: User) -> KnowledgeBase:
        """创建知识库"""
        kb = KnowledgeBase(
            owner_id=user.id,
            **data.model_dump(exclude_unset=True),
        )
        db.add(kb)
        await db.commit()
        await db.refresh(kb)
        return kb

    @staticmethod
    async def update(
        db: AsyncSession, kb_id: str, data: KnowledgeBaseUpdate, user: User
    ) -> KnowledgeBase:
        """更新知识库"""
        kb = await get_or_404(db, KnowledgeBase, kb_id, "知识库")
        if kb.owner_id != user.id:
            raise PermissionDeniedError("无权修改此知识库")
        for key, value in data.model_dump(exclude_unset=True).items():
            setattr(kb, key, value)
        await db.commit()
        await db.refresh(kb)
        return kb

    @staticmethod
    async def delete(db: AsyncSession, kb_id: str, user: User) -> None:
        """删除知识库及其文档"""
        kb = await get_or_404(db, KnowledgeBase, kb_id, "知识库")
        if kb.owner_id != user.id:
            raise PermissionDeniedError("无权删除此知识库")

        # 删除向量数据
        try:
            from app.services.vector_store import get_vector_store
            vector_store = get_vector_store()
            vector_store.delete_collection(kb_id)
            logger.info(f"已清理知识库向量数据: {kb_id}")
        except Exception as e:
            logger.warning(f"清理向量数据失败: {e}")

        await db.delete(kb)
        await db.commit()

    @staticmethod
    async def copy(db: AsyncSession, kb_id: str, user: User) -> KnowledgeBase:
        """复制知识库（包括文档记录，向量数据需要重新上传生成）"""
        source_kb = await get_or_404(db, KnowledgeBase, kb_id, "知识库")
        if not source_kb.allow_copy:
            raise PermissionDeniedError("此知识库不允许复制")

        # 复制文档记录
        source_docs = (
            await db.execute(
                select(Document).where(Document.knowledge_base_id == kb_id)
            )
        ).scalars().all()

        # 创建副本
        new_kb = KnowledgeBase(
            owner_id=user.id,
            name=f"{source_kb.name} (副本)",
            description=source_kb.description,
            embedding_model=source_kb.embedding_model,
            chunk_size=source_kb.chunk_size,
            chunk_overlap=source_kb.chunk_overlap,
            doc_count=len(source_docs),
        )
        db.add(new_kb)
        await db.flush()

        for doc in source_docs:
            # 如果源文档有文件路径，尝试复制文件并标记为待处理
            new_file_path = None
            new_status = "pending"
            if doc.file_path and os.path.exists(doc.file_path):
                import shutil
                new_dir = os.path.join(settings.UPLOAD_DIR, f"kb_{new_kb.id}")
                os.makedirs(new_dir, exist_ok=True)
                new_file_path = os.path.join(new_dir, f"{doc.id}.{doc.file_type}")
                try:
                    shutil.copy2(doc.file_path, new_file_path)
                except Exception:
                    new_file_path = None
                    new_status = "error"

            new_doc = Document(
                knowledge_base_id=new_kb.id,
                filename=doc.filename,
                file_type=doc.file_type,
                file_size=doc.file_size,
                file_path=new_file_path,
                status=new_status,
                chunk_count=0,
                error_message="源文件不存在，需重新上传" if new_status == "error" else None,
            )
            db.add(new_doc)

        source_kb.copy_count += 1

        await db.commit()
        await db.refresh(new_kb)
        return new_kb

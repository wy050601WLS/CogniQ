"""知识库 API"""
import logging
from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.models.user import User
from app.models.knowledge_base import KnowledgeBase
from app.schemas.knowledge_base import (
    KnowledgeBaseCreate,
    KnowledgeBaseUpdate,
    KnowledgeBaseResponse,
    KnowledgeBaseListResponse,
    KnowledgeBaseMarketplaceResponse,
)
from app.services.knowledge_base import KnowledgeBaseService
from app.deps import get_current_user

logger = logging.getLogger(__name__)
router = APIRouter()


@router.get("/my", response_model=KnowledgeBaseListResponse, summary="我的知识库")
async def list_my_knowledge_bases(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """获取当前用户的知识库列表"""
    items = await KnowledgeBaseService.list_by_owner(db, current_user.id)
    return KnowledgeBaseListResponse(items=items, total=len(items))


@router.get("/marketplace", response_model=KnowledgeBaseMarketplaceResponse, summary="知识库广场")
async def list_marketplace(db: AsyncSession = Depends(get_db)):
    """获取公开知识库列表"""
    items = await KnowledgeBaseService.list_public(db)
    return KnowledgeBaseMarketplaceResponse(items=items, total=len(items))


@router.post("", response_model=KnowledgeBaseResponse, status_code=201, summary="创建知识库")
async def create_knowledge_base(
    data: KnowledgeBaseCreate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """创建新知识库"""
    kb = await KnowledgeBaseService.create(db, data, current_user)
    logger.info(f"创建知识库: {kb.name} ({kb.id})")
    return kb


@router.get("/{kb_id}", response_model=KnowledgeBaseResponse, summary="获取知识库详情")
async def get_knowledge_base(
    kb_id: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """获取指定知识库详情（仅限登录用户）"""
    from app.utils.helpers import get_or_404
    kb = await get_or_404(db, KnowledgeBase, kb_id, "知识库")
    # 公开知识库或官方知识库可被任何登录用户查看，私有知识库仅所有者可查看
    if not kb.is_public and not kb.is_official and kb.owner_id != current_user.id:
        from app.exceptions import PermissionDeniedError
        raise PermissionDeniedError("无权查看此知识库")
    return kb


@router.put("/{kb_id}", response_model=KnowledgeBaseResponse, summary="更新知识库")
async def update_knowledge_base(
    kb_id: str,
    data: KnowledgeBaseUpdate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """更新知识库信息"""
    kb = await KnowledgeBaseService.update(db, kb_id, data, current_user)
    logger.info(f"更新知识库: {kb.id}")
    return kb


@router.delete("/{kb_id}", status_code=204, summary="删除知识库")
async def delete_knowledge_base(
    kb_id: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """删除知识库及其所有文档"""
    await KnowledgeBaseService.delete(db, kb_id, current_user)
    logger.info(f"删除知识库: {kb_id}")


@router.post("/{kb_id}/copy", response_model=KnowledgeBaseResponse, summary="复制知识库")
async def copy_knowledge_base(
    kb_id: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """复制公开知识库"""
    kb = await KnowledgeBaseService.copy(db, kb_id, current_user)
    logger.info(f"复制知识库: {kb_id} -> {kb.id}")
    return kb

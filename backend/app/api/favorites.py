"""收藏 API"""
import logging
from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from pydantic import BaseModel, Field

from app.core.database import get_db
from app.deps import get_current_user
from app.models.user import User
from app.models.favorite import Favorite
from app.models.knowledge_base import KnowledgeBase
from app.exceptions import NotFoundError, BadRequestError

logger = logging.getLogger(__name__)
router = APIRouter()


class AddFavoriteRequest(BaseModel):
    """添加收藏请求"""
    knowledge_base_id: str = Field(..., description="知识库ID")


@router.get("", summary="获取收藏列表")
async def list_favorites(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """获取当前用户的收藏列表"""
    result = await db.execute(
        select(Favorite, KnowledgeBase)
        .join(KnowledgeBase, Favorite.knowledge_base_id == KnowledgeBase.id)
        .where(Favorite.user_id == current_user.id)
        .order_by(Favorite.created_at.desc())
    )
    rows = result.all()
    return [
        {
            "id": fav.id,
            "knowledge_base_id": fav.knowledge_base_id,
            "knowledge_base": {
                "id": kb.id,
                "name": kb.name,
                "description": kb.description,
                "doc_count": kb.doc_count,
            },
            "created_at": fav.created_at,
        }
        for fav, kb in rows
    ]


@router.post("", status_code=201, summary="添加收藏")
async def add_favorite(
    data: AddFavoriteRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """收藏知识库"""
    kb_id = data.knowledge_base_id

    # 检查知识库是否存在
    kb = (await db.execute(select(KnowledgeBase).where(KnowledgeBase.id == kb_id))).scalar_one_or_none()
    if not kb:
        raise NotFoundError("知识库", kb_id)

    # 检查是否已收藏
    existing = (
        await db.execute(
            select(Favorite).where(
                Favorite.user_id == current_user.id,
                Favorite.knowledge_base_id == kb_id,
            )
        )
    ).scalar_one_or_none()
    if existing:
        raise BadRequestError("已经收藏过了")

    fav = Favorite(user_id=current_user.id, knowledge_base_id=kb_id)
    db.add(fav)
    await db.commit()
    await db.refresh(fav)
    return {"id": fav.id, "message": "收藏成功"}


@router.delete("/{fav_id}", status_code=204, summary="取消收藏")
async def remove_favorite(
    fav_id: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """取消收藏"""
    fav = (
        await db.execute(
            select(Favorite).where(
                Favorite.id == fav_id,
                Favorite.user_id == current_user.id,
            )
        )
    ).scalar_one_or_none()
    if not fav:
        raise NotFoundError("收藏", fav_id)
    await db.delete(fav)
    await db.commit()

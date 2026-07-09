"""标签 API"""
import logging
from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from pydantic import BaseModel, Field
from typing import Optional

from app.core.database import get_db
from app.deps import get_current_user
from app.models.user import User
from app.models.tag import Tag
from app.exceptions import NotFoundError, ValidationError

logger = logging.getLogger(__name__)
router = APIRouter()


class TagCreate(BaseModel):
    name: str = Field(..., min_length=1, max_length=50, description="标签名称")
    color: Optional[str] = Field("#3b82f6", description="标签颜色 (HEX)")


class TagResponse(BaseModel):
    id: str
    name: str
    color: Optional[str]

    class Config:
        from_attributes = True


@router.get("", response_model=list[TagResponse], summary="获取所有标签")
async def list_tags(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(select(Tag).order_by(Tag.name))
    return result.scalars().all()


@router.post("", response_model=TagResponse, status_code=201, summary="创建标签")
async def create_tag(
    data: TagCreate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    # 检查重名
    existing = await db.execute(select(Tag).where(Tag.name == data.name))
    if existing.scalar_one_or_none():
        raise ValidationError("标签名已存在")

    tag = Tag(name=data.name, color=data.color)
    db.add(tag)
    await db.commit()
    await db.refresh(tag)
    return tag


@router.delete("/{tag_id}", status_code=204, summary="删除标签")
async def delete_tag(
    tag_id: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    tag = (await db.execute(select(Tag).where(Tag.id == tag_id))).scalar_one_or_none()
    if not tag:
        raise NotFoundError("标签", tag_id)
    await db.delete(tag)
    await db.commit()

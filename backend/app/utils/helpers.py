"""工具函数"""
import logging
from typing import TypeVar, Type
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.exceptions import NotFoundError

logger = logging.getLogger(__name__)

ModelType = TypeVar("ModelType")


async def get_or_404(
    db: AsyncSession,
    model: Type[ModelType],
    id: str,
    name: str = "资源",
) -> ModelType:
    """获取对象，不存在则抛出 404"""
    result = await db.execute(select(model).where(model.id == id))
    obj = result.scalar_one_or_none()
    if not obj:
        raise NotFoundError(name, id)
    return obj

"""依赖注入"""
from typing import Optional
from fastapi import Depends, HTTPException, Header
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.core.database import get_db
from app.core.security import decode_token
from app.models.user import User
from app.exceptions import UnauthorizedError, PermissionDeniedError


async def get_current_user(
    authorization: Optional[str] = Header(None),
    db: AsyncSession = Depends(get_db),
) -> User:
    """获取当前登录用户"""
    if not authorization or not authorization.startswith("Bearer "):
        raise UnauthorizedError("未登录")

    token = authorization.split(" ")[1]
    payload = decode_token(token)

    if not payload or payload.get("type") != "access":
        raise UnauthorizedError("无效的 Token")

    user_id = payload.get("sub")
    result = await db.execute(select(User).where(User.id == user_id))
    user = result.scalar_one_or_none()

    if not user:
        raise UnauthorizedError("用户不存在")

    if user.status == "disabled":
        raise UnauthorizedError("账号已被禁用")

    return user


async def get_current_admin(
    current_user: User = Depends(get_current_user),
) -> User:
    """获取当前管理员"""
    if current_user.role != "admin":
        raise PermissionDeniedError("需要管理员权限")
    return current_user

"""管理后台 API"""
import logging
from fastapi import APIRouter, Depends, Request
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from pydantic import BaseModel, Field
from typing import Optional

from app.core.database import get_db
from app.deps import get_current_admin
from app.models.user import User
from app.models.document import Document
from app.models.conversation import Conversation, Message
from app.schemas.user import UserResponse
from app.schemas.document import DocumentResponse
from app.services.audit_log import log_action
from app.utils.helpers import get_or_404
from app.exceptions import BadRequestError, ValidationError

logger = logging.getLogger(__name__)
router = APIRouter()

# 允许的字段值
VALID_ROLES = {"user", "admin"}
VALID_STATUSES = {"active", "disabled"}


class UpdateUserRequest(BaseModel):
    """更新用户请求"""
    role: Optional[str] = Field(None, description="角色: user/admin")
    status: Optional[str] = Field(None, description="状态: active/disabled")
    nickname: Optional[str] = Field(None, description="昵称")
    avatar: Optional[str] = Field(None, description="头像URL")


# ===== 用户管理 =====

@router.get("/users", response_model=list[UserResponse], summary="获取用户列表")
async def list_users(
    admin: User = Depends(get_current_admin),
    db: AsyncSession = Depends(get_db),
):
    """获取所有用户列表"""
    result = await db.execute(select(User).order_by(User.created_at.desc()))
    return result.scalars().all()


@router.get("/users/{user_id}", response_model=UserResponse, summary="获取用户详情")
async def get_user(
    user_id: str,
    admin: User = Depends(get_current_admin),
    db: AsyncSession = Depends(get_db),
):
    """获取指定用户详情"""
    return await get_or_404(db, User, user_id, "用户")


@router.put("/users/{user_id}", response_model=UserResponse, summary="更新用户")
async def update_user(
    user_id: str,
    data: UpdateUserRequest,
    admin: User = Depends(get_current_admin),
    db: AsyncSession = Depends(get_db),
):
    """管理员更新用户信息（角色、状态等）"""
    user = await get_or_404(db, User, user_id, "用户")

    # 验证字段值
    update_data = data.model_dump(exclude_unset=True)
    if "role" in update_data and update_data["role"] not in VALID_ROLES:
        raise ValidationError(f"无效的角色值: {update_data['role']}，允许的值: {', '.join(VALID_ROLES)}")
    if "status" in update_data and update_data["status"] not in VALID_STATUSES:
        raise ValidationError(f"无效的状态值: {update_data['status']}，允许的值: {', '.join(VALID_STATUSES)}")

    # 不能禁用自己
    if user.id == admin.id and update_data.get("status") == "disabled":
        raise BadRequestError("不能禁用自己的账号")

    # 不能降级自己
    if user.id == admin.id and update_data.get("role") == "user":
        raise BadRequestError("不能降级自己的管理员角色")

    for key, value in update_data.items():
        if key == "role":
            user.role = value
        elif key == "status":
            user.status = value
        elif key == "nickname":
            user.nickname = value
        elif key == "avatar":
            user.avatar = value

    await db.commit()
    await db.refresh(user)

    # 记录操作日志
    await log_action(
        action="update",
        user_id=admin.id,
        username=admin.username,
        resource_type="user",
        resource_id=user.id,
        detail=f"更新用户 {user.username}: {update_data}",
    )

    return user


@router.delete("/users/{user_id}", status_code=204, summary="删除用户")
async def delete_user(
    user_id: str,
    admin: User = Depends(get_current_admin),
    db: AsyncSession = Depends(get_db),
):
    """删除用户"""
    user = await get_or_404(db, User, user_id, "用户")
    if user.id == admin.id:
        raise BadRequestError("不能删除自己的账号")

    username = user.username
    await db.delete(user)
    await db.commit()

    # 记录操作日志
    await log_action(
        action="delete",
        user_id=admin.id,
        username=admin.username,
        resource_type="user",
        resource_id=user_id,
        detail=f"删除用户 {username}",
    )


# ===== 文件管理 =====

@router.get("/files", response_model=list[DocumentResponse], summary="获取所有文件")
async def list_files(
    admin: User = Depends(get_current_admin),
    db: AsyncSession = Depends(get_db),
):
    """管理员获取所有文件"""
    result = await db.execute(select(Document).order_by(Document.created_at.desc()))
    return result.scalars().all()


@router.delete("/files/{doc_id}", status_code=204, summary="删除文件")
async def delete_file(
    doc_id: str,
    admin: User = Depends(get_current_admin),
    db: AsyncSession = Depends(get_db),
):
    """管理员删除任意文件"""
    doc = await get_or_404(db, Document, doc_id, "文件")

    # 清理向量数据
    try:
        from app.services.vector_store import get_vector_store
        vector_store = get_vector_store()
        vector_store.delete_documents(doc_id)
        logger.info(f"已清理文件向量数据: {doc_id}")
    except Exception as e:
        logger.warning(f"清理向量数据失败: {e}")

    await db.delete(doc)
    await db.commit()

    # 记录操作日志
    await log_action(
        action="delete",
        user_id=admin.id,
        username=admin.username,
        resource_type="document",
        resource_id=doc_id,
        detail=f"删除文件 {doc.filename}",
    )


# ===== 统计 =====

@router.get("/stats/overview", summary="总览统计")
async def stats_overview(
    admin: User = Depends(get_current_admin),
    db: AsyncSession = Depends(get_db),
):
    """获取系统总览统计"""
    user_count = (await db.execute(select(func.count(User.id)))).scalar() or 0
    file_count = (await db.execute(select(func.count(Document.id)))).scalar() or 0
    conv_count = (await db.execute(select(func.count(Conversation.id)))).scalar() or 0
    msg_count = (await db.execute(select(func.count(Message.id)))).scalar() or 0
    return {
        "user_count": user_count,
        "file_count": file_count,
        "conversation_count": conv_count,
        "message_count": msg_count,
    }


@router.get("/stats/users", summary="用户统计")
async def stats_users(
    admin: User = Depends(get_current_admin),
    db: AsyncSession = Depends(get_db),
):
    """获取用户注册统计"""
    result = await db.execute(
        select(
            func.date(User.created_at).label("date"),
            func.count(User.id).label("count"),
        ).group_by(func.date(User.created_at)).order_by(func.date(User.created_at))
    )
    return [{"date": str(row.date), "count": row.count} for row in result.all()]


@router.get("/stats/trends", summary="使用趋势")
async def stats_trends(
    admin: User = Depends(get_current_admin),
    db: AsyncSession = Depends(get_db),
):
    """获取对话使用趋势"""
    result = await db.execute(
        select(
            func.date(Conversation.created_at).label("date"),
            func.count(Conversation.id).label("count"),
        ).group_by(func.date(Conversation.created_at)).order_by(func.date(Conversation.created_at))
    )
    return [{"date": str(row.date), "count": row.count} for row in result.all()]

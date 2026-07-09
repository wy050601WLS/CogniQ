"""用户模式"""
from pydantic import BaseModel, ConfigDict, Field
from typing import Optional
from datetime import datetime


class UserResponse(BaseModel):
    """用户响应"""
    model_config = ConfigDict(from_attributes=True)

    id: str = Field(..., description="用户ID")
    username: str = Field(..., description="用户名")
    email: str = Field(..., description="邮箱")
    nickname: Optional[str] = Field(None, description="昵称")
    avatar: Optional[str] = Field(None, description="头像URL")
    role: str = Field(..., description="角色：user/admin")
    status: str = Field(..., description="状态：active/disabled")
    created_at: datetime = Field(..., description="创建时间")


class UserUpdateRequest(BaseModel):
    """用户更新请求"""
    nickname: Optional[str] = Field(None, max_length=50, description="昵称")
    avatar: Optional[str] = Field(None, max_length=255, description="头像URL")
    settings: Optional[dict] = Field(None, description="个人设置")


class ChangePasswordRequest(BaseModel):
    """修改密码请求"""
    old_password: str = Field(..., description="原密码")
    new_password: str = Field(..., min_length=6, max_length=100, description="新密码（至少6位）")

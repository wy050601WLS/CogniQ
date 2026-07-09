"""认证模式"""
from pydantic import BaseModel, Field, EmailStr
from typing import Optional
from app.schemas.user import UserResponse


class RegisterRequest(BaseModel):
    """注册请求"""
    username: str = Field(
        ...,
        min_length=3,
        max_length=50,
        description="用户名（3-50个字符）",
        examples=["testuser"]
    )
    email: EmailStr = Field(
        ...,
        description="邮箱地址",
        examples=["user@example.com"]
    )
    password: str = Field(
        ...,
        min_length=6,
        max_length=100,
        description="密码（至少6位）",
        examples=["123456"]
    )
    nickname: Optional[str] = Field(
        None,
        max_length=50,
        description="昵称（可选）",
        examples=["测试用户"]
    )


class LoginRequest(BaseModel):
    """登录请求"""
    username: str = Field(
        ...,
        description="用户名或邮箱",
        examples=["testuser"]
    )
    password: str = Field(
        ...,
        description="密码",
        examples=["123456"]
    )


class TokenResponse(BaseModel):
    """Token 响应"""
    access_token: str = Field(..., description="访问令牌")
    refresh_token: str = Field(..., description="刷新令牌")
    token_type: str = Field(default="bearer", description="令牌类型")
    user: UserResponse = Field(..., description="用户信息")


class RefreshTokenRequest(BaseModel):
    """刷新 Token 请求"""
    refresh_token: str = Field(..., description="刷新令牌")

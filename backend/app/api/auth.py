"""认证 API"""
import os
import time
import uuid
import logging
from fastapi import APIRouter, Depends, Request, UploadFile, File
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.config import settings
from app.core.database import get_db
from app.core.security import (
    hash_password,
    verify_password,
    create_access_token,
    create_refresh_token,
    decode_token,
)
from app.models.user import User
from app.schemas.auth import (
    RegisterRequest,
    LoginRequest,
    TokenResponse,
    RefreshTokenRequest,
)
from app.schemas.user import UserResponse, UserUpdateRequest, ChangePasswordRequest
from app.exceptions import ValidationError, NotFoundError
from app.deps import get_current_user

logger = logging.getLogger(__name__)
router = APIRouter()

# 简单的内存频率限制器
# key -> (尝试次数, 首次尝试时间)
_login_attempts: dict[str, tuple[int, float]] = {}
_MAX_LOGIN_ATTEMPTS = 10
_WINDOW_SECONDS = 300  # 5分钟窗口


def _check_rate_limit(key: str) -> bool:
    """检查是否超过频率限制，返回 True 表示允许"""
    now = time.time()
    if key in _login_attempts:
        count, first_time = _login_attempts[key]
        if now - first_time > _WINDOW_SECONDS:
            # 窗口过期，重置
            _login_attempts[key] = (1, now)
            return True
        if count >= _MAX_LOGIN_ATTEMPTS:
            return False
        _login_attempts[key] = (count + 1, first_time)
    else:
        _login_attempts[key] = (1, now)
    return True


@router.post("/register", response_model=TokenResponse, status_code=201, summary="用户注册")
async def register(data: RegisterRequest, db: AsyncSession = Depends(get_db)):
    """用户注册"""
    # 检查用户名
    result = await db.execute(select(User).where(User.username == data.username))
    if result.scalar_one_or_none():
        raise ValidationError("用户名已存在")

    # 检查邮箱
    result = await db.execute(select(User).where(User.email == data.email))
    if result.scalar_one_or_none():
        raise ValidationError("邮箱已被注册")

    # 创建用户
    user = User(
        username=data.username,
        email=data.email,
        password_hash=hash_password(data.password),
        nickname=data.nickname or data.username,
    )
    db.add(user)
    await db.commit()
    await db.refresh(user)

    # 生成 Token
    access_token = create_access_token({"sub": user.id, "role": user.role})
    refresh_token = create_refresh_token({"sub": user.id})

    logger.info(f"用户注册: {user.username} ({user.id})")

    return TokenResponse(
        access_token=access_token,
        refresh_token=refresh_token,
        user=UserResponse.model_validate(user),
    )


@router.post("/login", response_model=TokenResponse, summary="用户登录")
async def login(data: LoginRequest, request: Request, db: AsyncSession = Depends(get_db)):
    """用户登录（带频率限制）"""
    # 频率限制：基于 IP + 用户名
    client_ip = request.client.host if request.client else "unknown"
    rate_key = f"login:{client_ip}:{data.username}"
    if not _check_rate_limit(rate_key):
        raise ValidationError("登录尝试过于频繁，请 5 分钟后重试")

    # 查找用户
    result = await db.execute(
        select(User).where((User.username == data.username) | (User.email == data.username))
    )
    user = result.scalar_one_or_none()

    if not user or not verify_password(data.password, user.password_hash):
        raise ValidationError("用户名或密码错误")

    if user.status == "disabled":
        raise ValidationError("账号已被禁用")

    # 登录成功，重置该用户的频率计数
    _login_attempts.pop(rate_key, None)

    # 生成 Token
    access_token = create_access_token({"sub": user.id, "role": user.role})
    refresh_token = create_refresh_token({"sub": user.id})

    logger.info(f"用户登录: {user.username}")

    return TokenResponse(
        access_token=access_token,
        refresh_token=refresh_token,
        user=UserResponse.model_validate(user),
    )


@router.post("/refresh", response_model=TokenResponse, summary="刷新 Token")
async def refresh_token(data: RefreshTokenRequest, db: AsyncSession = Depends(get_db)):
    """刷新 Access Token"""
    payload = decode_token(data.refresh_token)
    if not payload or payload.get("type") != "refresh":
        raise ValidationError("无效的 Refresh Token")

    user_id = payload.get("sub")
    result = await db.execute(select(User).where(User.id == user_id))
    user = result.scalar_one_or_none()

    if not user:
        raise NotFoundError("用户", user_id)

    if user.status == "disabled":
        raise ValidationError("账号已被禁用")

    access_token = create_access_token({"sub": user.id, "role": user.role})
    new_refresh_token = create_refresh_token({"sub": user.id})

    return TokenResponse(
        access_token=access_token,
        refresh_token=new_refresh_token,
        user=UserResponse.model_validate(user),
    )


@router.get("/me", response_model=UserResponse, summary="获取当前用户")
async def get_me(current_user: User = Depends(get_current_user)):
    """获取当前登录用户信息"""
    return UserResponse.model_validate(current_user)


@router.put("/me", response_model=UserResponse, summary="更新个人信息")
async def update_me(
    data: UserUpdateRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """更新当前用户的个人信息"""
    if data.nickname is not None:
        current_user.nickname = data.nickname
    if data.avatar is not None:
        current_user.avatar = data.avatar
    if data.settings is not None:
        current_user.settings = data.settings

    await db.commit()
    await db.refresh(current_user)
    return UserResponse.model_validate(current_user)


@router.put("/password", summary="修改密码")
async def change_password(
    data: ChangePasswordRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """修改当前用户密码"""
    # 验证旧密码
    if not verify_password(data.old_password, current_user.password_hash):
        raise ValidationError("原密码错误")

    # 更新密码
    current_user.password_hash = hash_password(data.new_password)
    await db.commit()

    return {"message": "密码修改成功"}


@router.post("/avatar", summary="上传头像")
async def upload_avatar(
    file: UploadFile = File(...),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """上传用户头像"""
    # 验证文件类型
    allowed_types = {"image/jpeg", "image/png", "image/gif", "image/webp"}
    if file.content_type not in allowed_types:
        raise ValidationError("仅支持 JPG/PNG/GIF/WebP 格式的图片")

    # 验证文件大小（最大 5MB）
    content = await file.read()
    if len(content) > 5 * 1024 * 1024:
        raise ValidationError("头像文件大小不能超过 5MB")

    # 保存文件
    avatar_dir = os.path.join(settings.UPLOAD_DIR, "avatars")
    os.makedirs(avatar_dir, exist_ok=True)

    ext = file.filename.rsplit(".", 1)[-1] if "." in file.filename else "jpg"
    filename = f"{current_user.id}_{int(time.time())}.{ext}"
    file_path = os.path.join(avatar_dir, filename)

    with open(file_path, "wb") as f:
        f.write(content)

    # 更新用户头像 URL
    avatar_url = f"/api/uploads/avatars/{filename}"
    current_user.avatar = avatar_url
    await db.commit()
    await db.refresh(current_user)

    return {"avatar_url": avatar_url, "user": UserResponse.model_validate(current_user)}

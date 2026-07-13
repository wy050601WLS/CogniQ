"""API 路由"""
from fastapi import APIRouter
from app.api.auth import router as auth_router
from app.api.document import router as doc_router
from app.api.chat import router as chat_router
from app.api.settings import router as settings_router
from app.api.admin import router as admin_router
from app.api.feedback import router as feedback_router
from app.api.help import router as help_router
from app.api.tags import router as tags_router

api_router = APIRouter(prefix="/api")

# 公开路由（无需登录）
api_router.include_router(help_router, tags=["帮助"])

# 认证路由（无需登录）
api_router.include_router(auth_router, prefix="/auth", tags=["认证"])

# 需要登录的路由
api_router.include_router(doc_router, prefix="/files", tags=["文件"])
api_router.include_router(chat_router, tags=["聊天"])
api_router.include_router(settings_router, prefix="/settings", tags=["设置"])
api_router.include_router(feedback_router, prefix="/feedback", tags=["反馈"])
api_router.include_router(tags_router, prefix="/tags", tags=["标签"])

# 管理后台路由（需要管理员权限）
api_router.include_router(admin_router, prefix="/admin", tags=["管理后台"])

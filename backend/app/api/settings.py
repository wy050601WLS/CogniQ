"""设置 API"""
import logging
from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.deps import get_current_user, get_current_admin
from app.models.user import User
from app.schemas.settings import SettingsResponse, UpdateSettingsRequest
from app.services.settings import SettingsService

logger = logging.getLogger(__name__)
router = APIRouter()


@router.get("", response_model=SettingsResponse, summary="获取系统设置")
async def get_settings(db: AsyncSession = Depends(get_db)):
    """获取当前系统设置（公开接口）"""
    return await SettingsService.get_settings(db)


@router.get("/models", summary="获取可用模型列表")
async def list_models():
    """获取可用的 LLM 模型列表（公开接口）"""
    try:
        from app.services.llm import get_llm_service

        llm = get_llm_service()
        models = await llm.list_models()
        return {"models": models}
    except Exception as e:
        logger.warning(f"获取模型列表失败: {e}")
        return {"models": ["qwen2:7b"]}


@router.put("", summary="更新系统设置")
async def update_settings(
    data: UpdateSettingsRequest,
    current_user: User = Depends(get_current_admin),
    db: AsyncSession = Depends(get_db),
):
    """更新系统设置（仅管理员）"""
    await SettingsService.update_settings(db, data.model_dump(exclude_unset=True))
    logger.info(f"系统设置已更新 by {current_user.username}")
    return {"message": "设置已保存"}

"""设置服务"""
import logging
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.config import settings
from app.models.setting import Setting
from app.schemas.settings import SettingsResponse, LLMSettings, EmbeddingSettings, ChunkingSettings

logger = logging.getLogger(__name__)

# 设置键名与默认值的映射
SETTING_DEFAULTS = {
    "llm_provider": settings.LLM_PROVIDER,
    "ollama_model": settings.OLLAMA_MODEL,
    "openai_model": settings.OPENAI_MODEL,
    "openai_api_key": "",
    "embedding_provider": settings.EMBEDDING_PROVIDER,
    "embedding_model": settings.EMBEDDING_MODEL,
    "chunk_size": str(settings.DEFAULT_CHUNK_SIZE),
    "chunk_overlap": str(settings.DEFAULT_CHUNK_OVERLAP),
}


class SettingsService:
    """设置业务逻辑"""

    @staticmethod
    async def _load_all_settings(db: AsyncSession) -> dict[str, str]:
        """一次查询加载所有设置，返回 {key: value} 字典"""
        result = await db.execute(select(Setting))
        return {s.key: s.value for s in result.scalars().all()}

    @staticmethod
    async def get_setting_value(db: AsyncSession, key: str, default: str = "") -> str:
        """从数据库获取设置值"""
        result = await db.execute(select(Setting).where(Setting.key == key))
        setting = result.scalar_one_or_none()
        return setting.value if setting else default

    @staticmethod
    async def set_setting_value(
        db: AsyncSession, key: str, value: str, description: str = ""
    ) -> None:
        """保存设置值到数据库"""
        result = await db.execute(select(Setting).where(Setting.key == key))
        setting = result.scalar_one_or_none()
        if setting:
            setting.value = value
            if description:
                setting.description = description
        else:
            setting = Setting(key=key, value=value, description=description)
            db.add(setting)

    @staticmethod
    async def get_settings(db: AsyncSession) -> SettingsResponse:
        """获取所有设置（单次查询）"""
        all_settings = await SettingsService._load_all_settings(db)
        g = lambda key: all_settings.get(key, SETTING_DEFAULTS.get(key, ""))

        return SettingsResponse(
            llm=LLMSettings(
                provider=g("llm_provider"),
                ollama_model=g("ollama_model"),
                openai_model=g("openai_model"),
                openai_api_key="****" if g("openai_api_key") else "",
            ),
            embedding=EmbeddingSettings(
                provider=g("embedding_provider"),
                model=g("embedding_model"),
            ),
            chunking=ChunkingSettings(
                chunk_size=int(g("chunk_size")),
                chunk_overlap=int(g("chunk_overlap")),
            ),
        )

    @staticmethod
    async def update_settings(db: AsyncSession, data: dict) -> None:
        """更新设置（批量写入，单次 commit）"""
        if "llm" in data:
            llm = data["llm"]
            if "provider" in llm:
                await SettingsService.set_setting_value(db, "llm_provider", llm["provider"], "LLM 提供者")
            if "ollama_model" in llm:
                await SettingsService.set_setting_value(db, "ollama_model", llm["ollama_model"], "Ollama 模型")
            if "openai_model" in llm:
                await SettingsService.set_setting_value(db, "openai_model", llm["openai_model"], "OpenAI 模型")
            if "openai_api_key" in llm and llm["openai_api_key"] != "****":
                await SettingsService.set_setting_value(db, "openai_api_key", llm["openai_api_key"], "OpenAI API Key")

        if "embedding" in data:
            emb = data["embedding"]
            if "provider" in emb:
                await SettingsService.set_setting_value(db, "embedding_provider", emb["provider"], "嵌入提供者")
            if "model" in emb:
                await SettingsService.set_setting_value(db, "embedding_model", emb["model"], "嵌入模型")

        if "chunking" in data:
            chunk = data["chunking"]
            if "chunk_size" in chunk:
                await SettingsService.set_setting_value(db, "chunk_size", str(chunk["chunk_size"]), "分块大小")
            if "chunk_overlap" in chunk:
                await SettingsService.set_setting_value(db, "chunk_overlap", str(chunk["chunk_overlap"]), "分块重叠")

        await db.commit()

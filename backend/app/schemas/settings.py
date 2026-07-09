from pydantic import BaseModel, Field
from typing import Optional


class LLMSettings(BaseModel):
    provider: str = Field("ollama", description="LLM 提供者")
    ollama_model: Optional[str] = Field(None, description="Ollama 模型")
    openai_model: Optional[str] = Field(None, description="OpenAI 模型")
    openai_api_key: Optional[str] = Field(None, description="OpenAI API Key")


class EmbeddingSettings(BaseModel):
    provider: str = Field("sentence-transformers", description="嵌入提供者")
    model: Optional[str] = Field(None, description="嵌入模型")


class ChunkingSettings(BaseModel):
    chunk_size: int = Field(500, ge=100, le=2000, description="分块大小")
    chunk_overlap: int = Field(50, ge=0, le=500, description="分块重叠")


class SettingsResponse(BaseModel):
    llm: LLMSettings
    embedding: EmbeddingSettings
    chunking: ChunkingSettings


class UpdateSettingsRequest(BaseModel):
    """更新系统设置请求"""
    llm: Optional[LLMSettings] = None
    embedding: Optional[EmbeddingSettings] = None
    chunking: Optional[ChunkingSettings] = None

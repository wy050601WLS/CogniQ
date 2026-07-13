from pydantic import BaseModel, ConfigDict, Field
from typing import Optional, List
from datetime import datetime


class ChatRequest(BaseModel):
    conversation_id: Optional[str] = Field(None, description="对话ID，为空则创建新对话")
    message: str = Field(..., min_length=1, description="用户消息")
    stream: bool = Field(True, description="是否流式响应")


class SourceDocument(BaseModel):
    doc_id: str
    doc_filename: str  # 文件名
    chunk_id: str
    content: str
    score: float


class ChatResponse(BaseModel):
    conversation_id: str
    message_id: str
    content: str
    sources: List[SourceDocument] = []


class ConversationCreate(BaseModel):
    title: Optional[str] = "新对话"


class ConversationResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    title: str
    document_ids: Optional[list] = None
    created_at: datetime
    updated_at: datetime


class MessageResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    conversation_id: str
    role: str
    content: str
    sources: Optional[list]
    created_at: datetime

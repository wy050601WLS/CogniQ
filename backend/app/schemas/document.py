from pydantic import BaseModel, ConfigDict, Field
from typing import Optional, List
from datetime import datetime


class TagInfo(BaseModel):
    """标签信息"""
    id: str
    name: str
    color: Optional[str] = None


class DocumentResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    owner_id: str
    filename: str
    description: Optional[str] = None
    file_type: str
    file_size: int
    status: str
    error_message: Optional[str] = None
    chunk_count: int
    is_public: bool
    copy_count: int
    view_count: int
    version: int
    is_copied: bool = False
    created_at: datetime
    updated_at: datetime
    tags: List[TagInfo] = []
    uploader_name: Optional[str] = None  # 上传人名称


class DocumentUpdateRequest(BaseModel):
    """更新文件信息请求"""
    filename: Optional[str] = Field(None, description="文件名")
    description: Optional[str] = Field(None, description="文件描述")
    is_public: Optional[bool] = Field(None, description="是否公开")
    tag_ids: Optional[List[str]] = Field(None, description="标签ID列表")


class DocumentVersionResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    document_id: str
    version: int
    filename: str
    file_size: int
    chunk_count: int
    created_at: datetime

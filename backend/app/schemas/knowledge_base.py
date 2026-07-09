"""知识库模式"""
from pydantic import BaseModel, ConfigDict, Field
from typing import Optional
from datetime import datetime


class KnowledgeBaseCreate(BaseModel):
    """创建知识库请求"""
    name: str = Field(
        ...,
        min_length=1,
        max_length=255,
        description="知识库名称",
        examples=["Python 知识库"]
    )
    description: Optional[str] = Field(
        None,
        description="知识库描述",
        examples=["Python 编程语言相关知识"]
    )
    is_public: bool = Field(
        False,
        description="是否公开（公开后其他用户可查看）"
    )
    embedding_model: Optional[str] = Field(
        None,
        description="嵌入模型（默认使用系统配置）",
        examples=["BAAI/bge-small-zh-v1.5"]
    )
    chunk_size: Optional[int] = Field(
        None,
        ge=100,
        le=2000,
        description="分块大小（字符数）",
        examples=[500]
    )
    chunk_overlap: Optional[int] = Field(
        None,
        ge=0,
        le=500,
        description="分块重叠（字符数）",
        examples=[50]
    )


class KnowledgeBaseUpdate(BaseModel):
    """更新知识库请求"""
    name: Optional[str] = Field(None, min_length=1, max_length=255, description="知识库名称")
    description: Optional[str] = Field(None, description="知识库描述")
    is_public: Optional[bool] = Field(None, description="是否公开")
    allow_copy: Optional[bool] = Field(None, description="是否允许复制")


class KnowledgeBaseResponse(BaseModel):
    """知识库响应"""
    model_config = ConfigDict(from_attributes=True)

    id: str = Field(..., description="知识库ID")
    owner_id: str = Field(..., description="所有者ID")
    name: str = Field(..., description="知识库名称")
    description: Optional[str] = Field(None, description="描述")
    is_public: bool = Field(..., description="是否公开")
    is_official: bool = Field(..., description="是否官方")
    allow_copy: bool = Field(..., description="是否允许复制")
    copy_count: int = Field(..., description="复制次数")
    embedding_model: str = Field(..., description="嵌入模型")
    chunk_size: int = Field(..., description="分块大小")
    chunk_overlap: int = Field(..., description="分块重叠")
    doc_count: int = Field(..., description="文档数量")
    tags: list = Field(default_factory=list, description="标签列表")
    created_at: datetime = Field(..., description="创建时间")
    updated_at: datetime = Field(..., description="更新时间")


class KnowledgeBaseListResponse(BaseModel):
    """知识库列表响应"""
    items: list[KnowledgeBaseResponse] = Field(..., description="知识库列表")
    total: int = Field(..., description="总数")


class KnowledgeBaseMarketplaceResponse(BaseModel):
    """知识库广场响应"""
    items: list[KnowledgeBaseResponse] = Field(..., description="公开知识库列表")
    total: int = Field(..., description="总数")

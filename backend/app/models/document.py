import uuid
from datetime import datetime, timezone
from sqlalchemy import Column, String, Text, Integer, DateTime, Boolean, ForeignKey
from sqlalchemy.orm import relationship
from app.core.database import Base


class Document(Base):
    __tablename__ = "documents"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    owner_id = Column(String(36), ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    filename = Column(String(512), nullable=False)
    description = Column(Text, nullable=True)  # 文件描述（手动或AI生成）
    file_type = Column(String(32), nullable=False)
    file_size = Column(Integer, nullable=False)
    file_path = Column(String(1024), nullable=True)  # 磁盘上的存储路径
    status = Column(String(32), nullable=False, default="pending")  # pending/processing/completed/error
    error_message = Column(Text, nullable=True)
    chunk_count = Column(Integer, nullable=False, default=0)
    is_public = Column(Boolean, nullable=False, default=False)  # 是否公开
    copy_count = Column(Integer, nullable=False, default=0)  # 被复制次数
    view_count = Column(Integer, nullable=False, default=0)  # 被查看次数
    version = Column(Integer, nullable=False, default=1)  # 版本号
    is_copied = Column(Boolean, nullable=False, default=False)  # 是否为复制的文件（无修改权）
    created_at = Column(DateTime, nullable=False, default=lambda: datetime.now(timezone.utc))
    updated_at = Column(DateTime, nullable=False, default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))

    # 标签关系
    tags = relationship("Tag", secondary="document_tags", backref="documents", lazy="selectin")


class DocumentVersion(Base):
    __tablename__ = "document_versions"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    document_id = Column(String(36), ForeignKey("documents.id", ondelete="CASCADE"), nullable=False, index=True)
    version = Column(Integer, nullable=False)
    filename = Column(String(512), nullable=False)
    file_path = Column(String(1024), nullable=False)
    file_size = Column(Integer, nullable=False)
    chunk_count = Column(Integer, nullable=False, default=0)
    created_at = Column(DateTime, nullable=False, default=lambda: datetime.now(timezone.utc))

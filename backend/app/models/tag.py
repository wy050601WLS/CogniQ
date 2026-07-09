"""标签模型"""
import uuid
from datetime import datetime, timezone
from sqlalchemy import Column, String, DateTime, ForeignKey, Table
from app.core.database import Base

# 知识库-标签关联表
kb_tag_table = Table(
    "kb_tags",
    Base.metadata,
    Column("knowledge_base_id", String(36), ForeignKey("knowledge_bases.id", ondelete="CASCADE"), primary_key=True),
    Column("tag_id", String(36), ForeignKey("tags.id", ondelete="CASCADE"), primary_key=True),
)


class Tag(Base):
    __tablename__ = "tags"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    name = Column(String(50), nullable=False, unique=True, index=True)
    color = Column(String(7), nullable=True, default="#3b82f6")  # HEX 颜色
    created_at = Column(DateTime, nullable=False, default=lambda: datetime.now(timezone.utc))

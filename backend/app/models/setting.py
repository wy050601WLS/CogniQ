"""设置模型"""
from sqlalchemy import Column, String, Text
from app.core.database import Base


class Setting(Base):
    __tablename__ = "settings"

    key = Column(String(128), primary_key=True)
    value = Column(Text, nullable=False)
    description = Column(String(255), nullable=True)

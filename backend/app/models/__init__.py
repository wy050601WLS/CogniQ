"""模型注册"""
from app.core.database import Base
from app.models.user import User
from app.models.knowledge_base import KnowledgeBase
from app.models.document import Document
from app.models.conversation import Conversation, Message
from app.models.setting import Setting
from app.models.feedback import Feedback
from app.models.favorite import Favorite
from app.models.tag import Tag
from app.models.audit_log import AuditLog

__all__ = [
    "Base",
    "User",
    "KnowledgeBase",
    "Document",
    "Conversation",
    "Message",
    "Setting",
    "Feedback",
    "Favorite",
    "Tag",
    "AuditLog",
]

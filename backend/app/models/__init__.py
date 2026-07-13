"""模型注册"""
from app.core.database import Base
from app.models.user import User
from app.models.document import Document, DocumentVersion
from app.models.user_file import UserFile
from app.models.conversation import Conversation, Message
from app.models.setting import Setting
from app.models.feedback import Feedback
from app.models.tag import Tag
from app.models.audit_log import AuditLog

__all__ = [
    "Base",
    "User",
    "Document",
    "DocumentVersion",
    "UserFile",
    "Conversation",
    "Message",
    "Setting",
    "Feedback",
    "Tag",
    "AuditLog",
]

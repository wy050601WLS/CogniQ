"""操作日志服务"""
import logging
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.audit_log import AuditLog
from app.core.database import async_session

logger = logging.getLogger(__name__)


async def log_action(
    action: str,
    user_id: str = None,
    username: str = None,
    resource_type: str = None,
    resource_id: str = None,
    detail: str = None,
    ip_address: str = None,
):
    """记录操作日志"""
    try:
        async with async_session() as session:
            log = AuditLog(
                user_id=user_id,
                username=username,
                action=action,
                resource_type=resource_type,
                resource_id=resource_id,
                detail=detail,
                ip_address=ip_address,
            )
            session.add(log)
            await session.commit()
    except Exception as e:
        logger.warning(f"记录操作日志失败: {e}")

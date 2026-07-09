"""反馈 API"""
import logging
from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from pydantic import BaseModel, Field
from typing import Optional

from app.core.database import get_db
from app.deps import get_current_user
from app.models.user import User
from app.models.feedback import Feedback
from app.models.conversation import Conversation, Message
from app.exceptions import BadRequestError, NotFoundError, PermissionDeniedError

logger = logging.getLogger(__name__)
router = APIRouter()


class SubmitFeedbackRequest(BaseModel):
    """提交反馈请求"""
    message_id: str = Field(..., description="消息ID")
    conversation_id: str = Field(..., description="对话ID")
    rating: int = Field(..., ge=1, le=5, description="评分 1-5")
    comment: Optional[str] = Field(None, description="评论")


@router.post("", status_code=201, summary="提交反馈")
async def submit_feedback(
    data: SubmitFeedbackRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """提交消息反馈"""
    # 验证对话存在且属于当前用户
    conv = await db.execute(
        select(Conversation).where(Conversation.id == data.conversation_id)
    )
    conversation = conv.scalar_one_or_none()
    if not conversation:
        raise NotFoundError("对话", data.conversation_id)
    if conversation.user_id != current_user.id:
        raise PermissionDeniedError("无权对此对话提交反馈")

    # 验证消息存在且属于该对话
    msg = await db.execute(
        select(Message).where(
            Message.id == data.message_id,
            Message.conversation_id == data.conversation_id,
        )
    )
    message = msg.scalar_one_or_none()
    if not message:
        raise NotFoundError("消息", data.message_id)

    fb = Feedback(
        user_id=current_user.id,
        message_id=data.message_id,
        conversation_id=data.conversation_id,
        rating=data.rating,
        comment=data.comment,
    )
    db.add(fb)
    await db.commit()
    return {"message": "反馈已提交"}

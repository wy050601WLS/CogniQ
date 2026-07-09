"""文档 API"""
import logging
from fastapi import APIRouter, Depends, UploadFile, File
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.deps import get_current_user
from app.models.user import User
from app.schemas.document import DocumentResponse
from app.services.document import DocumentService

logger = logging.getLogger(__name__)
router = APIRouter()


@router.get(
    "/knowledge-bases/{kb_id}/documents",
    response_model=list[DocumentResponse],
    summary="获取文档列表",
)
async def list_documents(
    kb_id: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """获取知识库下的所有文档"""
    return await DocumentService.list_by_kb(db, kb_id, current_user.id)


@router.post(
    "/knowledge-bases/{kb_id}/documents/upload",
    response_model=DocumentResponse,
    status_code=201,
    summary="上传文档",
)
async def upload_document(
    kb_id: str,
    file: UploadFile = File(...),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """上传并处理文档"""
    doc = await DocumentService.upload_and_process(db, kb_id, file, current_user.id)
    logger.info(f"文档上传成功: {doc.filename} ({doc.id})")
    return doc


@router.get("/documents/{doc_id}", response_model=DocumentResponse, summary="获取文档详情")
async def get_document(
    doc_id: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """获取指定文档详情"""
    return await DocumentService.get_by_id(db, doc_id, current_user.id)


@router.delete("/documents/{doc_id}", status_code=204, summary="删除文档")
async def delete_document(
    doc_id: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """删除文档及其向量数据"""
    await DocumentService.delete(db, doc_id, current_user.id)
    logger.info(f"文档已删除: {doc_id}")

"""文件 API"""
import logging
from fastapi import APIRouter, Depends, UploadFile, File, Query, Form, HTTPException
from fastapi.responses import FileResponse
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from typing import List, Optional

from app.core.database import get_db
from app.deps import get_current_user
from app.models.user import User
from app.models.document import Document, DocumentVersion
from app.models.tag import Tag
from app.schemas.document import DocumentResponse, DocumentUpdateRequest, DocumentVersionResponse
from app.services.document import DocumentService
from app.exceptions import NotFoundError, PermissionDeniedError, ValidationError

logger = logging.getLogger(__name__)
router = APIRouter()


@router.get("", response_model=List[DocumentResponse], summary="我的文件列表")
async def list_my_files(
    page: int = Query(1, ge=1, description="页码"),
    page_size: int = Query(20, ge=1, le=100, description="每页数量"),
    tag_id: Optional[str] = Query(None, description="按标签筛选"),
    file_type: Optional[str] = Query(None, description="按文件类型筛选"),
    search: Optional[str] = Query(None, description="搜索文件名"),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """获取当前用户的文件列表（包含拥有的文件和引用的文件）"""
    from app.models.user_file import UserFile
    from sqlalchemy.orm import selectinload

    # 获取拥有的文件 ID
    owned_query = select(Document.id).where(Document.owner_id == current_user.id)
    owned_result = await db.execute(owned_query)
    owned_ids = [row[0] for row in owned_result.all()]

    # 获取引用的文件 ID
    ref_query = select(UserFile.document_id).where(UserFile.user_id == current_user.id)
    ref_result = await db.execute(ref_query)
    ref_ids = [row[0] for row in ref_result.all()]

    # 合并 ID 列表
    all_ids = list(set(owned_ids + ref_ids))

    if not all_ids:
        return []

    # 查询文件（带标签预加载）
    query = select(Document).options(selectinload(Document.tags)).where(Document.id.in_(all_ids))

    if tag_id:
        query = query.join(Document.tags).where(Tag.id == tag_id)
    if file_type:
        query = query.where(Document.file_type == file_type)
    if search:
        query = query.where(Document.filename.contains(search))

    query = query.order_by(Document.updated_at.desc())
    offset = (page - 1) * page_size
    query = query.offset(offset).limit(page_size)

    result = await db.execute(query)
    docs = result.scalars().all()

    # 批量查询上传人名称
    owner_ids = list(set([doc.owner_id for doc in docs]))
    if owner_ids:
        from app.models.user import User as UserModel
        users_result = await db.execute(
            select(UserModel.id, UserModel.nickname, UserModel.username).where(UserModel.id.in_(owner_ids))
        )
        user_map = {}
        for row in users_result.all():
            user_map[row[0]] = row[1] or row[2]  # nickname 优先，否则用 username
    else:
        user_map = {}

    # 构建响应数据
    owned_set = set(owned_ids)
    ref_set = set(ref_ids)
    response_data = []
    for doc in docs:
        doc_dict = {
            "id": doc.id,
            "owner_id": doc.owner_id,
            "filename": doc.filename,
            "description": doc.description,
            "file_type": doc.file_type,
            "file_size": doc.file_size,
            "status": doc.status,
            "error_message": doc.error_message,
            "chunk_count": doc.chunk_count,
            "is_public": doc.is_public,
            "copy_count": doc.copy_count,
            "view_count": doc.view_count,
            "version": doc.version,
            "is_reference": doc.id in ref_set and doc.id not in owned_set,
            "created_at": doc.created_at,
            "updated_at": doc.updated_at,
            "tags": [{"id": t.id, "name": t.name, "color": t.color} for t in doc.tags],
            "uploader_name": user_map.get(doc.owner_id, "未知"),
        }
        response_data.append(doc_dict)

    return response_data


@router.post("/upload", response_model=DocumentResponse, status_code=201, summary="上传文件")
async def upload_file(
    file: UploadFile = File(...),
    description: Optional[str] = Form(None, description="文件描述"),
    tag_ids: Optional[str] = Form(None, description="标签ID列表，逗号分隔"),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """上传文件"""
    # 解析 tag_ids
    tag_id_list = tag_ids.split(",") if tag_ids else []
    doc = await DocumentService.upload_and_process(db, file, current_user.id, description, tag_id_list)
    logger.info(f"文件上传成功: {doc.filename} ({doc.id})")
    return doc


@router.get("/shared", response_model=List[DocumentResponse], summary="公开文件列表")
async def list_shared_files(
    page: int = Query(1, ge=1, description="页码"),
    page_size: int = Query(20, ge=1, le=100, description="每页数量"),
    search: Optional[str] = Query(None, description="搜索文件名"),
    db: AsyncSession = Depends(get_db),
):
    """获取公开文件列表（知识广场）"""
    from sqlalchemy.orm import selectinload

    query = select(Document).options(selectinload(Document.tags)).where(Document.is_public == True)

    if search:
        query = query.where(Document.filename.contains(search))

    query = query.order_by(Document.view_count.desc())
    offset = (page - 1) * page_size
    query = query.offset(offset).limit(page_size)

    result = await db.execute(query)
    docs = result.scalars().all()

    # 批量查询上传人名称
    owner_ids = list(set([doc.owner_id for doc in docs]))
    if owner_ids:
        from app.models.user import User as UserModel
        users_result = await db.execute(
            select(UserModel.id, UserModel.nickname, UserModel.username).where(UserModel.id.in_(owner_ids))
        )
        user_map = {}
        for row in users_result.all():
            user_map[row[0]] = row[1] or row[2]
    else:
        user_map = {}

    # 构建响应数据
    response_data = []
    for doc in docs:
        doc_dict = {
            "id": doc.id,
            "owner_id": doc.owner_id,
            "filename": doc.filename,
            "description": doc.description,
            "file_type": doc.file_type,
            "file_size": doc.file_size,
            "status": doc.status,
            "error_message": doc.error_message,
            "chunk_count": doc.chunk_count,
            "is_public": doc.is_public,
            "copy_count": doc.copy_count,
            "view_count": doc.view_count,
            "version": doc.version,
            "is_copied": doc.is_copied,
            "created_at": doc.created_at,
            "updated_at": doc.updated_at,
            "tags": [{"id": t.id, "name": t.name, "color": t.color} for t in doc.tags],
            "uploader_name": user_map.get(doc.owner_id, "未知"),
        }
        response_data.append(doc_dict)

    return response_data


@router.get("/{doc_id}", response_model=DocumentResponse, summary="文件详情")
async def get_file(
    doc_id: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """获取文件详情"""
    doc = await DocumentService.get_by_id(db, doc_id, current_user.id)
    # 增加查看次数
    doc.view_count += 1
    await db.commit()
    return doc


@router.put("/{doc_id}", response_model=DocumentResponse, summary="更新文件信息")
async def update_file(
    doc_id: str,
    data: DocumentUpdateRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """更新文件信息（名称、描述、标签、公开状态）"""
    doc = await DocumentService.update_info(db, doc_id, data, current_user.id)
    return doc


@router.delete("/{doc_id}", status_code=204, summary="删除文件")
async def delete_file(
    doc_id: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """删除文件及其向量数据"""
    await DocumentService.delete(db, doc_id, current_user.id)
    logger.info(f"文件已删除: {doc_id}")


@router.put("/{doc_id}/replace", response_model=DocumentResponse, summary="替换文件内容")
async def replace_file(
    doc_id: str,
    file: UploadFile = File(...),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """替换文件内容（创建新版本）"""
    doc = await DocumentService.replace_file(db, doc_id, file, current_user.id)
    return doc


@router.post("/{doc_id}/description", summary="AI 生成文件描述")
async def generate_description(
    doc_id: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """使用 AI 生成文件描述"""
    doc = await DocumentService.generate_description(db, doc_id, current_user.id)
    return {"description": doc.description}


@router.get("/{doc_id}/versions", response_model=List[DocumentVersionResponse], summary="文件版本历史")
async def list_versions(
    doc_id: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """获取文件版本历史"""
    # 验证文件存在且属于当前用户
    doc = await DocumentService.get_by_id(db, doc_id, current_user.id)

    result = await db.execute(
        select(DocumentVersion)
        .where(DocumentVersion.document_id == doc_id)
        .order_by(DocumentVersion.version.desc())
    )
    return result.scalars().all()


@router.post("/{doc_id}/rollback/{version}", response_model=DocumentResponse, summary="回滚到指定版本")
async def rollback_version(
    doc_id: str,
    version: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """回滚到指定版本"""
    doc = await DocumentService.rollback_version(db, doc_id, version, current_user.id)
    return doc


@router.post("/{doc_id}/add", summary="添加公开文件到我的文件")
async def add_file(
    doc_id: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """添加公开文件到我的文件列表（创建引用关系）"""
    result = await DocumentService.add_file(db, doc_id, current_user.id)
    return result


@router.get("/{doc_id}/download", summary="下载文件")
async def download_file(
    doc_id: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """下载文件"""
    doc = await DocumentService.get_by_id(db, doc_id, current_user.id)
    if not doc.file_path:
        raise ValidationError("文件不存在")
    return FileResponse(
        path=doc.file_path,
        filename=doc.filename,
        media_type="application/octet-stream"
    )


@router.get("/{doc_id}/preview", summary="文件内容预览")
async def preview_file(
    doc_id: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """预览文件内容"""
    doc = await DocumentService.get_by_id(db, doc_id, current_user.id)
    preview_content = await DocumentService.get_preview(db, doc_id)
    return {"filename": doc.filename, "file_type": doc.file_type, "content": preview_content}

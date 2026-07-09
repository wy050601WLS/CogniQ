"""知识问答系统 - FastAPI 应用入口"""
import logging
from contextlib import asynccontextmanager
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.openapi.docs import get_swagger_ui_html

from app.config import settings
from app.api.router import api_router
from app.core.database import init_db
from app.exceptions import AppException
from app.middleware.logging import LoggingMiddleware
from app.middleware.error_handler import ErrorHandlerMiddleware

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)
logger = logging.getLogger("app")


@asynccontextmanager
async def lifespan(app: FastAPI):
    """应用生命周期"""
    logger.info("正在启动知识问答系统...")
    await init_db()
    logger.info("数据库初始化完成")
    yield
    logger.info("系统关闭")


app = FastAPI(
    title="知识问答系统 API",
    description="""
## 知识问答系统

基于 RAG（检索增强生成）技术的智能知识问答平台。

### 功能特性
- 🔐 用户认证（JWT）
- 📚 知识库管理
- 📄 文档上传与解析
- 💬 智能问答（流式响应）
- ⭐ 收藏与反馈
- 👥 知识库共享

### 技术栈
- **后端**: Python + FastAPI + SQLAlchemy
- **向量库**: ChromaDB
    """,
    version="1.0.0",
    lifespan=lifespan,
    docs_url=None,
    redoc_url=None,
)

# 中间件（按顺序添加，后添加的先执行）
app.add_middleware(LoggingMiddleware)
app.add_middleware(ErrorHandlerMiddleware)
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 挂载路由
app.include_router(api_router)

# 挂载上传文件静态目录
import os
os.makedirs(settings.UPLOAD_DIR, exist_ok=True)
app.mount("/api/uploads", StaticFiles(directory=settings.UPLOAD_DIR), name="uploads")


@app.exception_handler(AppException)
async def app_exception_handler(request: Request, exc: AppException):
    """自定义应用异常处理"""
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "error": {
                "code": exc.code,
                "message": exc.message,
                "detail": exc.detail,
            }
        },
    )


@app.get("/", tags=["系统"])
async def root():
    """系统入口"""
    return {
        "message": "知识问答系统 API",
        "version": "1.0.0",
        "docs": "/docs",
        "redoc": "/redoc",
    }


@app.get("/health", tags=["系统"])
async def health():
    """健康检查"""
    return {"status": "ok"}


@app.get("/docs", include_in_schema=False)
async def custom_swagger_ui():
    """自定义 Swagger UI"""
    return get_swagger_ui_html(
        openapi_url=app.openapi_url,
        title="知识问答系统 API 文档",
        swagger_js_url="https://cdn.jsdelivr.net/npm/swagger-ui-dist@5/swagger-ui-bundle.js",
        swagger_css_url="https://cdn.jsdelivr.net/npm/swagger-ui-dist@5/swagger-ui.css",
    )

"""重建向量数据 - 为所有文档生成向量"""
import asyncio
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from sqlalchemy import select
from app.core.database import async_session
from app.services.vector_store import get_vector_store
from app.models.document import Document
from app.models.knowledge_base import KnowledgeBase
from app.config import settings


async def rebuild():
    """重建所有文档的向量"""
    os.makedirs(settings.UPLOAD_DIR, exist_ok=True)

    # 创建测试文档
    test_docs = {
        "python_basics.md": "# Python 基础\n\nPython 是一种高级编程语言，语法简洁，易于学习。",
        "python_web.md": "# Python Web\n\nFlask 和 Django 是常用的 Web 框架。",
        "ml_intro.md": "# 机器学习\n\n机器学习是 AI 的分支，包括监督学习和无监督学习。",
    }

    for filename, content in test_docs.items():
        file_path = os.path.join(settings.UPLOAD_DIR, filename)
        if not os.path.exists(file_path):
            with open(file_path, "w", encoding="utf-8") as f:
                f.write(content)
            print(f"创建文件: {filename}")

    vector_store = get_vector_store()

    async with async_session() as db:
        # 获取所有知识库
        kb_result = await db.execute(select(KnowledgeBase))
        kbs = kb_result.scalars().all()

        if not kbs:
            print("没有知识库，请先创建")
            return

        # 使用第一个知识库
        kb = kbs[0]
        print(f"\n处理知识库: {kb.name}")

        # 获取或创建集合
        collection = vector_store.get_or_create_collection(kb.id)
        existing_count = collection.count()
        print(f"当前向量数: {existing_count}")

        # 创建文档记录
        doc_files = [
            ("python_basics.md", "md", "Python 基础教程"),
            ("python_web.md", "md", "Python Web 开发"),
            ("ml_intro.md", "md", "机器学习入门"),
        ]

        for filename, file_type, desc in doc_files:
            file_path = os.path.join(settings.UPLOAD_DIR, filename)
            if not os.path.exists(file_path):
                print(f"  文件不存在: {filename}")
                continue

            # 检查文档是否已存在
            doc_result = await db.execute(
                select(Document).where(Document.filename == filename)
            )
            existing_doc = doc_result.scalar_one_or_none()

            if existing_doc:
                doc = existing_doc
                print(f"  使用现有文档: {filename}")
            else:
                file_size = os.path.getsize(file_path)
                doc = Document(
                    knowledge_base_id=kb.id,
                    filename=filename,
                    file_type=file_type,
                    file_size=file_size,
                    status="pending",
                )
                db.add(doc)
                await db.flush()
                print(f"  创建文档: {filename}")

            # 处理文档生成向量
            try:
                from app.services.chat import process_document

                chunk_count = process_document(
                    kb_id=kb.id,
                    doc_id=doc.id,
                    file_path=file_path,
                    chunk_size=kb.chunk_size,
                    chunk_overlap=kb.chunk_overlap,
                )
                doc.status = "completed"
                doc.chunk_count = chunk_count
                print(f"    成功: {chunk_count} 个分块")
            except Exception as e:
                doc.status = "error"
                doc.error_message = str(e)
                print(f"    失败: {str(e)[:60]}")

        await db.commit()

        # 验证
        print("\n=== 验证结果 ===")
        collection = vector_store.get_or_create_collection(kb.id)
        print(f"向量总数: {collection.count()}")

        # 测试查询
        results = vector_store.query(kb.id, "Python", n_results=2)
        print(f"查询 'Python' 结果: {len(results)} 条")
        for i, r in enumerate(results):
            print(f"  {i+1}. 相似度: {r['score']:.3f}")
            print(f"     内容: {r['content'][:80]}...")


if __name__ == "__main__":
    asyncio.run(rebuild())

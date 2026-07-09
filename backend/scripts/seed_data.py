"""种子数据 - 生成测试文档并处理"""
import asyncio
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.core.database import async_session, init_db
from app.core.security import hash_password
from app.models.user import User
from app.models.knowledge_base import KnowledgeBase
from app.models.document import Document
from app.config import settings
from sqlalchemy import select

# 测试文档内容
TEST_DOCUMENTS = {
    "python_basics.md": """# Python 编程基础

## 什么是 Python
Python 是一种广泛使用的高级编程语言，由 Guido van Rossum 于 1991 年首次发布。

## 主要特点
1. 简洁易读：语法清晰，使用缩进表示代码块
2. 解释型语言：无需编译，直接运行
3. 动态类型：变量不需要声明类型
4. 跨平台：支持 Windows、Linux、macOS

## 基本语法
```python
# 变量赋值
name = "Python"
version = 3.12

# 条件语句
if version > 3:
    print("这是 Python 3")

# 循环
for i in range(5):
    print(i)
```

## 常用数据类型
- 列表 (list): [1, 2, 3]
- 字典 (dict): {"key": "value"}
- 元组 (tuple): (1, 2, 3)
- 集合 (set): {1, 2, 3}
""",

    "python_web.md": """# Python Web 开发

## Web 框架
Python 有多个流行的 Web 框架：

### Django
- 全功能框架
- 内置 ORM、Admin、认证
- 适合大型项目

### Flask
- 轻量级框架
- 灵活扩展
- 适合小型项目和 API

### FastAPI
- 现代异步框架
- 自动生成 API 文档
- 高性能

## 示例代码
```python
# FastAPI 示例
from fastapi import FastAPI
app = FastAPI()

@app.get("/")
async def root():
    return {"message": "Hello World"}
```

## 数据库集成
- SQLAlchemy: ORM 框架
- PyMySQL: MySQL 驱动
- Redis: 缓存
""",

    "machine_learning.md": """# 机器学习基础

## 什么是机器学习
机器学习是人工智能的一个分支，使计算机能够从数据中学习。

## 主要类型
1. 监督学习：有标签数据
2. 无监督学习：无标签数据
3. 强化学习：通过奖励学习

## 常用算法
- 线性回归
- 决策树
- 随机森林
- 神经网络
- 支持向量机

## Python 库
- Scikit-learn：传统机器学习
- TensorFlow：深度学习
- PyTorch：深度学习
- Pandas：数据处理
- NumPy：数值计算
""",

    "deep_learning.md": """# 深度学习入门

## 什么是深度学习
深度学习是机器学习的一个子领域，使用多层神经网络。

## 神经网络结构
- 输入层：接收原始数据
- 隐藏层：特征提取
- 输出层：产生预测

## 常见网络类型
1. CNN：卷积神经网络，用于图像
2. RNN：循环神经网络，用于序列
3. Transformer：注意力机制，用于 NLP

## 应用场景
- 图像识别
- 自然语言处理
- 语音识别
- 推荐系统
""",
}


async def seed():
    """创建种子数据"""
    os.makedirs(settings.UPLOAD_DIR, exist_ok=True)

    await init_db()

    async with async_session() as db:
        # 检查是否已有用户
        result = await db.execute(select(User).where(User.username == "admin"))
        if result.scalar_one_or_none():
            print("数据库已有数据，跳过初始化")
            return

        print("开始创建种子数据...")

        # 创建用户
        users = [
            User(
                username="admin",
                email="admin@example.com",
                password_hash=hash_password("admin123"),
                nickname="管理员",
                role="admin",
            ),
            User(
                username="zhangsan",
                email="zhangsan@example.com",
                password_hash=hash_password("123456"),
                nickname="张三",
                role="user",
            ),
            User(
                username="lisi",
                email="lisi@example.com",
                password_hash=hash_password("123456"),
                nickname="李四",
                role="user",
            ),
        ]
        db.add_all(users)
        await db.flush()

        # 创建知识库
        kb = KnowledgeBase(
            owner_id=users[0].id,
            name="Python 编程指南",
            description="Python 编程语言学习资料",
            is_public=True,
        )
        db.add(kb)
        await db.flush()

        # 创建文档并写入文件
        for filename, content in TEST_DOCUMENTS.items():
            # 写入文件
            file_path = os.path.join(settings.UPLOAD_DIR, filename)
            with open(file_path, "w", encoding="utf-8") as f:
                f.write(content)

            doc = Document(
                knowledge_base_id=kb.id,
                filename=filename,
                file_type="md",
                file_size=len(content.encode()),
                status="pending",
            )
            db.add(doc)

        await db.commit()
        print(f"创建完成: 1 个用户, 1 个知识库, {len(TEST_DOCUMENTS)} 个文档")

        # 处理文档生成向量
        print()
        print("开始处理文档生成向量...")
        from app.services.chat import process_document

        result = await db.execute(
            select(Document).where(Document.knowledge_base_id == kb.id)
        )
        docs = result.scalars().all()

        for doc in docs:
            file_path = os.path.join(settings.UPLOAD_DIR, doc.filename)
            try:
                chunk_count = process_document(
                    kb_id=kb.id,
                    doc_id=doc.id,
                    file_path=file_path,
                    chunk_size=kb.chunk_size,
                    chunk_overlap=kb.chunk_overlap,
                )
                doc.status = "completed"
                doc.chunk_count = chunk_count
                print(f"  成功: {doc.filename} ({chunk_count} 个分块)")
            except Exception as e:
                doc.status = "error"
                doc.error_message = str(e)
                print(f"  失败: {doc.filename} ({e})")

        await db.commit()
        print()
        print("种子数据创建完成！")

        # 验证
        from app.services.vector_store import get_vector_store
        vs = get_vector_store()
        collection = vs.get_or_create_collection(kb.id)
        print(f"向量数量: {collection.count()}")


if __name__ == "__main__":
    asyncio.run(seed())

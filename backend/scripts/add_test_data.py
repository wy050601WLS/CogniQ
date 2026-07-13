"""添加测试数据"""
import asyncio
import uuid
import os
import shutil
from datetime import datetime, timezone

from app.core.database import async_session, engine, Base
from app.models.user import User
from app.models.document import Document, DocumentVersion
from app.models.tag import Tag
from app.models.conversation import Conversation, Message
from app.core.security import hash_password
from app.config import settings


async def add_data():
    """添加测试数据"""
    # 创建测试目录
    test_dir = os.path.join(settings.UPLOAD_DIR, "test_data")
    os.makedirs(test_dir, exist_ok=True)

    async with async_session() as session:
        # 检查是否已有数据
        from sqlalchemy import select, func
        result = await session.execute(select(func.count(Document.id)))
        if result.scalar() > 0:
            print("数据库已有数据，跳过添加")
            return

        # 获取 admin 用户
        result = await session.execute(select(User).where(User.username == "admin"))
        admin = result.scalar_one_or_none()
        if not admin:
            print("未找到 admin 用户")
            return

        print(f"添加测试数据给用户: {admin.username}")

        # 创建标签
        tags_data = [
            ("Python", "#3776ab"),
            ("机器学习", "#ff6b6b"),
            ("数据分析", "#4ecdc4"),
            ("深度学习", "#9b59b6"),
            ("Web开发", "#3498db"),
        ]
        tags = []
        for name, color in tags_data:
            tag = Tag(name=name, color=color)
            session.add(tag)
            tags.append(tag)
        await session.flush()
        print(f"创建了 {len(tags)} 个标签")

        # 创建测试文档
        test_files = [
            {
                "filename": "Python基础教程.md",
                "content": "# Python 基础教程\n\n## 1. 变量和数据类型\n\nPython 支持多种数据类型：\n- 整数 (int)\n- 浮点数 (float)\n- 字符串 (str)\n- 布尔值 (bool)\n\n## 2. 控制结构\n\n### if 语句\n```python\nif condition:\n    # do something\n```\n\n### for 循环\n```python\nfor item in list:\n    # do something\n```\n\n## 3. 函数\n\n```python\ndef function_name(parameters):\n    return result\n```",
                "tags": ["Python"],
            },
            {
                "filename": "机器学习入门.md",
                "content": "# 机器学习入门\n\n## 什么是机器学习？\n\n机器学习是人工智能的一个分支，它使计算机能够从数据中学习，而无需显式编程。\n\n## 主要类型\n\n1. **监督学习**：使用标记数据训练\n2. **无监督学习**：发现数据中的模式\n3. **强化学习**：通过试错学习\n\n## 常用算法\n\n- 线性回归\n- 决策树\n- 随机森林\n- 神经网络\n\n## Python 库\n\n- scikit-learn\n- TensorFlow\n- PyTorch",
                "tags": ["机器学习"],
            },
            {
                "filename": "数据分析指南.md",
                "content": "# 数据分析指南\n\n## 工具介绍\n\n### NumPy\n用于数值计算的基础库。\n\n### Pandas\n用于数据处理和分析。\n\n```python\nimport pandas as pd\ndf = pd.read_csv('data.csv')\n```\n\n### Matplotlib\n用于数据可视化。\n\n```python\nimport matplotlib.pyplot as plt\nplt.plot(x, y)\nplt.show()\n```\n\n## 分析流程\n\n1. 数据收集\n2. 数据清洗\n3. 探索性分析\n4. 建模分析\n5. 结果可视化",
                "tags": ["数据分析"],
            },
            {
                "filename": "深度学习基础.md",
                "content": "# 深度学习基础\n\n## 什么是深度学习？\n\n深度学习是机器学习的一个子集，使用多层神经网络来学习数据的层次化表示。\n\n## 核心概念\n\n### 神经网络\n- 输入层\n- 隐藏层\n- 输出层\n\n### 激活函数\n- ReLU\n- Sigmoid\n- Tanh\n\n## 常见架构\n\n1. CNN（卷积神经网络）\n2. RNN（循环神经网络）\n3. Transformer\n\n## 应用场景\n\n- 图像识别\n- 自然语言处理\n- 语音识别",
                "tags": ["深度学习"],
            },
            {
                "filename": "Web开发入门.md",
                "content": "# Web 开发入门\n\n## 前端技术\n\n### HTML\n网页的结构。\n\n### CSS\n网页的样式。\n\n### JavaScript\n网页的行为。\n\n## 后端技术\n\n### Node.js\n基于 Chrome V8 引擎的 JavaScript 运行时。\n\n### Django\nPython Web 框架。\n\n### FastAPI\n现代、快速的 Python Web 框架。\n\n## 开发流程\n\n1. 需求分析\n2. 设计\n3. 开发\n4. 测试\n5. 部署",
                "tags": ["Web开发"],
            },
            {
                "filename": "数据结构与算法.md",
                "content": "# 数据结构与算法\n\n## 基础数据结构\n\n### 数组\n连续存储的线性结构。\n\n### 链表\n非连续存储的线性结构。\n\n### 栈\n后进先出（LIFO）。\n\n### 队列\n先进先出（FIFO）。\n\n## 常用算法\n\n### 排序算法\n- 冒泡排序\n- 快速排序\n- 归并排序\n\n### 搜索算法\n- 二分搜索\n- 深度优先搜索\n- 广度优先搜索\n\n## 复杂度分析\n\n- O(1)：常数时间\n- O(log n)：对数时间\n- O(n)：线性时间\n- O(n log n)：线性对数时间",
                "tags": ["Python"],
            },
        ]

        doc_ids = []
        for file_data in test_files:
            # 创建文件
            file_path = os.path.join(test_dir, f"{uuid.uuid4()}.md")
            with open(file_path, "w", encoding="utf-8") as f:
                f.write(file_data["content"])

            # 创建文档记录
            doc = Document(
                owner_id=admin.id,
                filename=file_data["filename"],
                description=f"测试文档：{file_data['filename']}",
                file_type="md",
                file_size=len(file_data["content"].encode("utf-8")),
                file_path=file_path,
                status="completed",
                chunk_count=1,
                is_public=True,
                version=1,
            )
            session.add(doc)
            await session.flush()
            doc_ids.append(doc.id)

            # 添加标签
            for tag_name in file_data["tags"]:
                for tag in tags:
                    if tag.name == tag_name:
                        doc.tags.append(tag)

        print(f"创建了 {len(test_files)} 个测试文档")

        # 创建测试对话
        conv = Conversation(
            user_id=admin.id,
            title="测试对话",
        )
        session.add(conv)
        await session.flush()

        # 添加测试消息
        messages = [
            Message(
                conversation_id=conv.id,
                role="user",
                content="Python 是什么？",
            ),
            Message(
                conversation_id=conv.id,
                role="assistant",
                content="Python 是一种广泛使用的高级编程语言，以其简洁易读的语法和强大的功能而闻名。",
                sources=[{"doc_id": doc_ids[0], "content": "Python 基础教程", "score": 0.85}],
            ),
        ]
        for msg in messages:
            session.add(msg)

        await session.commit()
        print(f"测试数据添加完成！")
        print(f"- 用户: {admin.username}")
        print(f"- 标签: {len(tags)} 个")
        print(f"- 文档: {len(test_files)} 个")
        print(f"- 对话: 1 个")


if __name__ == "__main__":
    asyncio.run(add_data())

"""添加更多测试数据"""
import asyncio
import uuid
import os
from datetime import datetime, timezone

from sqlalchemy import select
from sqlalchemy.orm import selectinload
from app.core.database import async_session
from app.models.user import User
from app.models.document import Document
from app.models.tag import Tag
from app.config import settings


async def add_more_data():
    """添加更多测试数据"""
    # 创建测试目录
    test_dir = os.path.join(settings.UPLOAD_DIR, "test_data")
    os.makedirs(test_dir, exist_ok=True)

    async with async_session() as session:
        # 获取 admin 用户
        result = await session.execute(select(User).where(User.username == "admin"))
        admin = result.scalar_one_or_none()
        if not admin:
            print("未找到 admin 用户")
            return

        # 检查是否已有标签
        result = await session.execute(select(Tag))
        existing_tags = {t.name: t for t in result.scalars().all()}

        # 创建新标签
        new_tags = [
            ("Java", "#f89820"),
            ("JavaScript", "#f7df1e"),
            ("数据库", "#336791"),
            ("网络安全", "#e74c3c"),
        ]
        tags = dict(existing_tags)
        for name, color in new_tags:
            if name not in tags:
                tag = Tag(name=name, color=color)
                session.add(tag)
                tags[name] = tag
        await session.flush()

        # 创建新的测试文档
        test_files = [
            {
                "filename": "Java编程入门.md",
                "content": "# Java 编程入门\n\n## 1. Java 简介\n\nJava 是一种面向对象的编程语言，广泛应用于企业级开发。\n\n## 2. 基本语法\n\n### 变量声明\n```java\nint age = 25;\nString name = \"John\";\n```\n\n### 控制结构\n```java\nif (condition) {\n    // do something\n}\n\nfor (int i = 0; i < 10; i++) {\n    // do something\n}\n```\n\n## 3. 面向对象\n\n- 类和对象\n- 继承\n- 多态\n- 封装",
                "tags": ["Java"],
                "public": True,
            },
            {
                "filename": "JavaScript基础.md",
                "content": "# JavaScript 基础\n\n## 1. 变量\n\n```javascript\nlet name = 'John';\nconst age = 25;\n```\n\n## 2. 函数\n\n```javascript\nfunction greet(name) {\n    return `Hello, ${name}!`;\n}\n\nconst greet = (name) => `Hello, ${name}!`;\n```\n\n## 3. 异步编程\n\n```javascript\nasync function fetchData() {\n    const response = await fetch(url);\n    const data = await response.json();\n    return data;\n}\n```",
                "tags": ["JavaScript"],
                "public": True,
            },
            {
                "filename": "数据库设计原理.md",
                "content": "# 数据库设计原理\n\n## 1. 关系型数据库\n\n### 表设计\n- 主键\n- 外键\n- 索引\n\n### 范式\n- 第一范式 (1NF)\n- 第二范式 (2NF)\n- 第三范式 (3NF)\n\n## 2. SQL 基础\n\n```sql\nSELECT * FROM users WHERE age > 18;\nINSERT INTO users (name, email) VALUES ('John', 'john@example.com');\nUPDATE users SET name = 'Jane' WHERE id = 1;\nDELETE FROM users WHERE id = 1;\n```\n\n## 3. 索引优化\n\n- B-Tree 索引\n- 哈希索引\n- 全文索引",
                "tags": ["数据库"],
                "public": True,
            },
            {
                "filename": "网络安全基础.md",
                "content": "# 网络安全基础\n\n## 1. 常见攻击\n\n### SQL 注入\n使用参数化查询防止。\n\n### XSS 攻击\n对用户输入进行过滤和转义。\n\n### CSRF 攻击\n使用 Token 验证。\n\n## 2. 安全实践\n\n- 使用 HTTPS\n- 密码哈希存储\n- 输入验证\n- 权限控制\n\n## 3. 安全工具\n\n- OWASP ZAP\n- Nmap\n- Burp Suite",
                "tags": ["网络安全"],
                "public": True,
            },
            {
                "filename": "Linux命令行教程.md",
                "content": "# Linux 命令行教程\n\n## 1. 基本命令\n\n### 文件操作\n```bash\nls -la          # 列出文件\ncd /path        # 切换目录\ncp file1 file2  # 复制文件\nmv file1 file2  # 移动文件\nrm file         # 删除文件\n```\n\n### 文本处理\n```bash\ngrep pattern file   # 搜索\ncat file            # 查看文件\nhead -n 10 file     # 查看前10行\ntail -n 10 file     # 查看后10行\n```\n\n## 2. 权限管理\n\n```bash\nchmod 755 file  # 修改权限\nchown user file # 修改所有者\n```\n\n## 3. 进程管理\n\n```bash\nps aux          # 查看进程\nkill PID        # 终止进程\ntop             # 系统监控\n```",
                "tags": ["Python"],
                "public": False,
            },
        ]

        doc_count = 0
        for file_data in test_files:
            # 检查是否已存在同名文档
            result = await session.execute(
                select(Document).where(Document.filename == file_data["filename"])
            )
            if result.scalar_one_or_none():
                print(f"文档已存在: {file_data['filename']}")
                continue

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
                is_public=file_data.get("public", False),
                version=1,
            )
            session.add(doc)
            await session.flush()

            # 添加标签（直接操作关联表）
            from app.models.tag import document_tag_table
            for tag_name in file_data["tags"]:
                if tag_name in tags:
                    tag_id = tags[tag_name].id
                    await session.execute(
                        document_tag_table.insert().values(
                            document_id=doc.id,
                            tag_id=tag_id
                        )
                    )

            doc_count += 1

        await session.commit()
        print(f"添加了 {doc_count} 个新测试文档")
        print("测试数据添加完成！")


if __name__ == "__main__":
    asyncio.run(add_more_data())

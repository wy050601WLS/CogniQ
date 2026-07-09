# 知识问答系统

基于 RAG（检索增强生成）技术的智能知识问答平台。

## 功能特性

- 🔐 用户认证（JWT）
- 📚 知识库管理（创建、编辑、删除）
- 📄 文档上传与解析（PDF、Word、Markdown、TXT、HTML）
- 💬 智能问答（流式响应、来源引用）
- ⭐ 收藏与反馈
- 👥 知识库共享
- 📊 数据统计（管理端）

## 技术栈

### 后端
- Python 3.10+
- FastAPI
- SQLAlchemy（异步）
- MySQL
- ChromaDB（向量存储）
- Ollama（本地 LLM）

### 前端
- Vue 3
- Vite
- Element Plus
- Pinia

## 项目结构

```
knowledge-qa/
├── backend/              # 后端 API（端口 8000）
├── user-web/             # 用户端前端（端口 5175）
├── admin-web/            # 管理端前端（端口 5174）
├── SETUP.md              # 环境搭建文档
└── README.md             # 项目说明
```

## 快速开始

### 1. 环境准备

参考 `SETUP.md` 安装以下依赖：
- Python 3.10+
- Node.js 18+
- MySQL 5.7+
- Ollama

### 2. 后端启动

```bash
cd backend

# 安装依赖
pip install -r requirements.txt

# 配置数据库（编辑 .env 文件）
# 初始化数据库和测试数据
python scripts/seed_data.py

# 启动后端
python -m uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```

### 3. 用户前端启动

```bash
cd user-web

# 安装依赖
npm install

# 启动开发服务器
npm run dev
```

访问 http://localhost:5175

### 4. 管理后台启动

```bash
cd admin-web

# 安装依赖
npm install

# 启动开发服务器
npm run dev
```

访问 http://localhost:5174

## 测试账号

| 角色 | 用户名 | 密码 |
|------|--------|------|
| 管理员 | admin | admin123 |
| 普通用户 | zhangsan | 123456 |
| 普通用户 | lisi | 123456 |

## API 文档

启动后端后访问 http://localhost:8000/docs 查看 API 文档。

## 项目功能

### 用户端
- 首页：统计概览、推荐知识库、快捷操作
- 智能问答：选择知识库进行对话，支持流式响应和来源引用
- 我的知识库：创建和管理个人知识库
- 知识库广场：浏览和复制公开知识库
- 对话历史：查看和管理历史对话
- 我的收藏：管理收藏的知识库
- 个人中心：修改个人信息和密码

### 管理端
- 仪表盘：系统数据概览
- 用户管理：查看、禁用、删除用户
- 知识库管理：查看和删除所有知识库
- 文档管理：查看和删除所有文档
- 数据统计：用户增长和对话趋势
- 系统设置：配置 LLM、嵌入模型等参数

## License

MIT

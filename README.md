# 知识问答系统

> 基于 RAG 技术的智能知识问答平台

[![Python](https://img.shields.io/badge/Python-3.10+-blue.svg)](https://python.org)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.100+-green.svg)](https://fastapi.tiangolo.com)
[![Vue](https://img.shields.io/badge/Vue-3.3+-brightgreen.svg)](https://vuejs.org)
[![License](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

---

## 一、项目简介

### 1.1 项目定位

**知识问答系统（Knowledge QA）** 是一个基于 RAG（检索增强生成）技术的智能知识问答平台。用户可以上传文档到知识库，系统会自动解析、分块、向量化并存储，然后通过 AI 模型对用户的问题进行检索增强生成回答。

### 1.2 核心价值

| 价值 | 说明 |
|------|------|
| **知识管理** | 支持 PDF、Word、Markdown、TXT、HTML 等多种格式文档的上传、解析和管理 |
| **智能问答** | 基于 RAG 技术，AI 可以根据知识库内容精准回答问题，减少幻觉 |
| **来源引用** | 每个回答都标注参考来源，确保信息可追溯、可验证 |
| **多轮对话** | 支持上下文记忆，理解用户追问意图，实现自然对话 |
| **知识共享** | 支持公开知识库，用户可以浏览、复制他人的知识库 |

### 1.3 目标用户

- **企业团队**：构建企业内部知识库，提升知识管理效率
- **研究人员**：管理学术论文和研究资料，快速检索相关信息
- **学生群体**：整理学习资料，通过问答方式巩固知识
- **内容创作者**：管理创作素材，辅助内容生成

---

## 二、功能特性

### 2.1 用户端功能

| 功能模块 | 功能说明 |
|----------|----------|
| **智能问答** | 选择知识库进行对话，支持流式响应和来源引用 |
| **知识库管理** | 创建、编辑、删除个人知识库，设置可见性 |
| **文档管理** | 上传多格式文档，查看处理状态和分块信息 |
| **知识库广场** | 浏览和复制公开知识库，发现优质内容 |
| **对话历史** | 查看、搜索、删除历史对话，支持导出 |
| **收藏功能** | 收藏感兴趣的知识库，方便快速访问 |
| **个人中心** | 修改个人信息、头像、密码 |

### 2.2 管理端功能

| 功能模块 | 功能说明 |
|----------|----------|
| **仪表盘** | 系统数据概览，用户数、知识库数、文档数、消息数 |
| **用户管理** | 查看用户列表，禁用/启用用户，删除用户 |
| **知识库管理** | 查看所有知识库，删除违规知识库 |
| **文档管理** | 查看所有文档，删除违规文档 |
| **数据统计** | 用户增长趋势、对话使用趋势 |
| **系统设置** | 配置 LLM、嵌入模型、分块参数等 |

### 2.3 技术特性

| 特性 | 说明 |
|------|------|
| **RAG 检索增强** | 基于向量检索的精准问答，减少 AI 幻觉 |
| **流式响应** | SSE 实时输出，打字机效果，用户体验流畅 |
| **多轮对话** | 支持上下文记忆，理解追问意图 |
| **多格式支持** | PDF、Word、Markdown、TXT、HTML 文档解析 |
| **异步架构** | FastAPI 异步框架，高并发处理能力 |
| **安全认证** | JWT 双 Token 认证，Token 轮换机制 |

---

## 三、技术架构

### 3.1 整体架构

```
┌─────────────────────────────────────────────────────────────────┐
│                         前端层                                   │
│  ┌──────────────────┐         ┌──────────────────┐             │
│  │    用户端         │         │    管理端         │             │
│  │  Vue 3 + Element  │         │  Vue 3 + Element  │             │
│  │     Plus          │         │     Plus          │             │
│  │   (Port 5175)    │         │   (Port 5174)    │             │
│  └──────────────────┘         └──────────────────┘             │
└─────────────────────────────────────────────────────────────────┘
                                │
                                ▼
┌─────────────────────────────────────────────────────────────────┐
│                         API 网关层                               │
│                    FastAPI (Port 8000)                           │
│  ┌─────────────────────────────────────────────────────────┐   │
│  │  认证模块 │ 知识库模块 │ 文档模块 │ 聊天模块 │ 管理模块  │   │
│  └─────────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────────┘
                                │
          ┌─────────────────────┼─────────────────────┐
          ▼                     ▼                     ▼
┌──────────────────┐  ┌──────────────────┐  ┌──────────────────┐
│      MySQL       │  │     ChromaDB     │  │      Ollama      │
│    (关系数据)     │  │    (向量数据)     │  │    (LLM 服务)    │
│                  │  │                  │  │                  │
│  用户/知识库/     │  │  文档 Embedding   │  │   Qwen2:7b      │
│  文档/对话/消息   │  │    向量存储       │  │   本地推理       │
└──────────────────┘  └──────────────────┘  └──────────────────┘
```

### 3.2 技术选型

| 类别 | 选型 | 备选方案 | 选择理由 |
|------|------|----------|----------|
| Web 框架 | **FastAPI** | Django, Flask | 异步支持、自动文档、高性能 |
| ORM | **SQLAlchemy** | Tortoise ORM | 成熟稳定、社区活跃 |
| 数据库 | **MySQL** | PostgreSQL, SQLite | 生态完善、运维简单 |
| 向量库 | **ChromaDB** | Milvus, Pinecone | 轻量级、本地部署 |
| LLM | **Ollama** | OpenAI API | 隐私保护、零成本 |
| 前端框架 | **Vue 3** | React, Angular | 学习曲线平缓、中文生态 |
| UI 组件 | **Element Plus** | Ant Design Vue | 组件丰富、文档完善 |
| 状态管理 | **Pinia** | Vuex | 更简洁的 API |

### 3.3 数据流

```
用户提问 → 向量化 → 向量检索 → 构建 Prompt → LLM 生成 → 流式返回
    │          │          │           │           │          │
    │    Embedding    ChromaDB    检索结果    Ollama    SSE
    │    模型         余弦相似度  +对话历史   Qwen2:7b  实时输出
    ▼          ▼          ▼           ▼           ▼          ▼
```

---

## 四、数据库设计

### 4.1 核心表结构

| 表名 | 说明 | 核心字段 |
|------|------|----------|
| **users** | 用户表 | id, username, email, password_hash, role, status |
| **knowledge_bases** | 知识库表 | id, owner_id, name, is_public, chunk_size |
| **documents** | 文档表 | id, knowledge_base_id, filename, status, file_path |
| **conversations** | 对话表 | id, user_id, knowledge_base_id, title |
| **messages** | 消息表 | id, conversation_id, role, content, sources |
| **feedbacks** | 反馈表 | id, user_id, message_id, rating, comment |
| **favorites** | 收藏表 | id, user_id, knowledge_base_id |
| **tags** | 标签表 | id, name, color |

### 4.2 数据关系

```
users 1──N knowledge_bases 1──N documents
  │
  └──1──N conversations 1──N messages
                │
                └──1──N feedbacks
                
users 1──N favorites N──1 knowledge_bases
```

---

## 五、安全设计

### 5.1 认证安全

| 安全措施 | 实现方式 |
|----------|----------|
| JWT 双 Token | Access Token (60分钟) + Refresh Token (7天) |
| Token 轮换 | Refresh Token 使用后立即失效，防止重放攻击 |
| 密码哈希 | PBKDF2 + 随机盐值，100,000 次迭代 |
| 时序攻击防护 | hmac.compare_digest() 常量时间比较 |
| 频率限制 | 基于 IP 的登录/注册频率限制（5分钟10次） |

### 5.2 数据安全

| 安全措施 | 实现方式 |
|----------|----------|
| XSS 防护 | DOMPurify 消毒所有 HTML 输出 |
| SQL 注入防护 | SQLAlchemy ORM 参数化查询 |
| 文件上传验证 | 类型白名单 + 大小限制（50MB） |
| CORS 配置 | 限制跨域来源 |

### 5.3 运行时安全

| 安全措施 | 实现方式 |
|----------|----------|
| 接口文档保护 | 生产环境禁用 Swagger UI |
| JWT 密钥检查 | 生产环境强制要求安全密钥 |
| 错误信息脱敏 | 不暴露内部异常类型 |
| 操作审计 | 记录关键操作日志 |

---

## 六、快速开始

### 6.1 环境要求

| 软件 | 版本要求 |
|------|---------|
| Python | >= 3.10 |
| Node.js | >= 18 |
| MySQL | >= 5.7 |
| Ollama | 最新版本 |

### 6.2 安装步骤

**1. 克隆项目**
```bash
git clone https://github.com/wy050601WLS/CogniQ.git
cd CogniQ
```

**2. 后端启动**
```bash
cd backend

# 创建虚拟环境
python -m venv venv
venv\Scripts\activate  # Windows
# source venv/bin/activate  # macOS/Linux

# 安装依赖
pip install -r requirements.txt

# 配置环境变量
cp .env.example .env
# 编辑 .env 文件，配置数据库密码

# 初始化数据库
python scripts/seed_data.py

# 启动后端
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

**3. 用户端启动**
```bash
cd user-web
npm install
npm run dev
# 访问 http://localhost:5175
```

**4. 管理端启动**
```bash
cd admin-web
npm install
npm run dev
# 访问 http://localhost:5174
```

### 6.3 测试账号

| 角色 | 用户名 | 密码 |
|------|--------|------|
| 管理员 | admin | admin123 |
| 普通用户 | zhangsan | 123456 |
| 普通用户 | lisi | 123456 |

---

## 七、项目结构

```
knowledge-qa/
├── backend/                    # 后端 API 服务
│   ├── app/
│   │   ├── api/               # API 路由层
│   │   ├── core/              # 核心模块（数据库、安全、分块）
│   │   ├── services/          # 业务逻辑层
│   │   ├── models/            # 数据模型层
│   │   ├── schemas/           # Pydantic 数据模式
│   │   ├── middleware/         # 中间件
│   │   └── main.py            # 应用入口
│   └── requirements.txt
│
├── user-web/                   # 用户端前端
│   └── src/
│       ├── views/             # 页面组件
│       ├── api/               # API 调用层
│       ├── stores/            # Pinia 状态管理
│       └── router/            # 路由配置
│
├── admin-web/                  # 管理端前端
│   └── src/
│       ├── views/             # 页面组件
│       ├── api/               # API 调用层
│       └── stores/            # Pinia 状态管理
│
├── ARCHITECTURE.md             # 系统架构文档
├── FEATURE_NOTES.md            # 功能实现笔记
├── PROJECT_STRUCTURE.md        # 项目结构详解
├── ROADMAP.md                  # 功能扩展规划
├── SETUP.md                    # 环境搭建指南
└── README.md                   # 本文件
```

---

## 八、API 文档

启动后端后访问 http://localhost:8000/docs 查看 API 文档。

### 核心 API

| 模块 | 端点 | 说明 |
|------|------|------|
| 认证 | POST /api/auth/login | 用户登录 |
| 认证 | POST /api/auth/register | 用户注册 |
| 知识库 | GET /api/knowledge-bases/my | 我的知识库 |
| 知识库 | POST /api/knowledge-bases | 创建知识库 |
| 文档 | POST /api/knowledge-bases/{id}/documents/upload | 上传文档 |
| 聊天 | POST /api/chat | 发送消息（支持流式） |
| 对话 | GET /api/conversations | 对话列表 |

---

## 九、项目亮点

### 技术亮点
1. **RAG 检索增强生成**：基于向量检索的精准问答，减少 AI 幻觉
2. **流式响应架构**：SSE 实时输出，用户体验像 ChatGPT 一样流畅
3. **多轮对话支持**：上下文记忆，理解追问意图
4. **异步高性能**：FastAPI 异步框架 + 线程池优化
5. **本地化部署**：Ollama 本地 LLM，保护数据隐私

### 安全亮点
1. **JWT 双 Token 认证**：Access Token + Refresh Token 轮换机制
2. **密码安全存储**：PBKDF2 + 盐值 + 常量时间比较
3. **频率限制**：基于 IP 的登录/注册频率限制
4. **XSS 防护**：DOMPurify 消毒所有 HTML 输出

---

## 十、未来规划

### 短期（1-2周）
- [ ] 多轮对话记忆优化
- [ ] 对话导出功能增强
- [ ] 引用追溯优化

### 中期（1-2月）
- [ ] 知识图谱集成
- [ ] 知识库版本控制
- [ ] 标签系统完善

### 长期（3-6月）
- [ ] 多租户架构
- [ ] API 开放平台
- [ ] 多模态支持

---

## 十一、相关文档

| 文档 | 说明 |
|------|------|
| [ARCHITECTURE.md](ARCHITECTURE.md) | 系统架构详解 |
| [FEATURE_NOTES.md](FEATURE_NOTES.md) | 功能实现笔记（含面试准备） |
| [PROJECT_STRUCTURE.md](PROJECT_STRUCTURE.md) | 项目结构详解 |
| [ROADMAP.md](ROADMAP.md) | 功能扩展规划 |
| [SETUP.md](SETUP.md) | 环境搭建指南 |

---

## 十二、License

MIT

---

## 十三、联系方式

- **GitHub**: https://github.com/wy050601WLS/CogniQ
- **Issues**: https://github.com/wy050601WLS/CogniQ/issues

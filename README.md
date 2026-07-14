# 知识问答系统（CogniQ）

> 基于 RAG 技术的智能知识问答平台

[![Python](https://img.shields.io/badge/Python-3.10+-blue.svg)](https://python.org)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.100+-green.svg)](https://fastapi.tiangolo.com)
[![Vue](https://img.shields.io/badge/Vue-3.4+-brightgreen.svg)](https://vuejs.org)
[![License](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

---

## 一、项目简介

### 1.1 项目定位

**知识问答系统（CogniQ）** 是一个基于 RAG（检索增强生成）技术的智能知识问答平台。用户可以直接上传文档，系统会自动解析、分块、向量化并存储，然后通过 AI 模型对用户的问题进行检索增强生成回答。系统支持文件级别的权限控制、知识共享（引用模式）和多维度文件管理。

### 1.2 核心价值

| 价值 | 说明 |
|------|------|
| **直接文件管理** | 支持 PDF、Word、Markdown、TXT、HTML 等多种格式文档的上传、解析和管理，无需创建知识库 |
| **智能问答** | 基于 RAG 技术，AI 自动匹配用户最相关文件进行精准问答 |
| **来源引用** | 每个回答都标注参考来源文件，确保信息可追溯 |
| **多轮对话** | 支持上下文记忆，理解用户追问意图 |
| **知识共享** | 知识广场浏览公开文件，一键添加引用到个人文件列表 |
| **文件引用模式** | 引用文件可查看/删除但不可修改，节省存储空间避免数据冗余 |

### 1.3 目标用户

- **企业团队**：构建企业内部知识管理平台，提升知识管理效率
- **研究人员**：管理学术论文和研究资料，快速检索相关信息
- **学生群体**：整理学习资料，通过问答方式巩固知识
- **内容创作者**：管理创作素材，辅助内容生成

---

## 二、功能特性

### 2.1 用户端功能

| 功能模块 | 功能说明 |
|----------|----------|
| **智能问答** | 自动匹配最相关文件进行对话，支持流式响应和来源引用 |
| **我的文件** | 上传/编辑/删除/替换文件，支持多维度筛选（文件格式、上传人、标签）和排序 |
| **文件详情** | 查看文件信息、标签管理、内容预览、版本历史、替换文件 |
| **知识广场** | 浏览公开文件，一键添加引用到我的文件列表（引用模式） |
| **对话历史** | 查看、搜索、删除历史对话 |
| **帮助中心** | 分类帮助文档，支持搜索和 Markdown 渲染 |
| **个人中心** | 修改个人信息、头像、密码 |
| **深色模式** | 支持浅色/深色主题切换 |

### 2.2 管理端功能

| 功能模块 | 功能说明 |
|----------|----------|
| **仪表盘** | 系统数据概览，用户数、文件数、消息数 |
| **用户管理** | 查看用户列表，禁用/启用用户，删除用户 |
| **文件管理** | 查看所有文件，删除违规文件 |
| **数据统计** | 用户增长趋势、对话使用趋势 |
| **系统设置** | 配置 LLM、嵌入模型、分块参数等 |

### 2.3 技术特性

| 特性 | 说明 |
|------|------|
| **RAG 检索增强** | 基于向量检索的精准问答，减少 AI 幻觉 |
| **流式响应** | SSE 实时输出，打字机效果，超时保护（2分钟） |
| **多轮对话** | 支持上下文记忆，理解追问意图 |
| **多格式支持** | PDF、Word、Markdown、TXT、HTML 文档解析 |
| **异步架构** | FastAPI 异步框架，高并发处理能力 |
| **安全认证** | JWT 双 Token 认证，Token 自动刷新机制 |
| **文件引用** | 知识广场添加引用而非复制，节省存储空间 |
| **深色模式** | 全站深色模式支持，CSS 变量方案 |

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
│  │  认证模块 │ 文件模块 │ 聊天模块 │ 标签模块 │ 管理模块    │   │
│  └─────────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────────┘
                                │
          ┌─────────────────────┼─────────────────────┐
          ▼                     ▼                     ▼
┌──────────────────┐  ┌──────────────────┐  ┌──────────────────┐
│      MySQL       │  │     ChromaDB     │  │      Ollama      │
│    (关系数据)     │  │    (向量数据)     │  │    (LLM 服务)    │
│                  │  │                  │  │                  │
│  用户/文件/      │  │  文档 Embedding   │  │   Qwen2:7b      │
│  对话/消息/标签  │  │    向量存储       │  │   本地推理       │
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
| Embedding | **BGE-small-zh** | text2vec | 中文语义理解优秀 |
| 前端框架 | **Vue 3** | React, Angular | 学习曲线平缓、中文生态 |
| UI 组件 | **Element Plus** | Ant Design Vue | 组件丰富、文档完善 |
| 状态管理 | **Pinia** | Vuex | 更简洁的 API |

### 3.3 数据流

```
用户提问 → 向量化 → 跨文件向量检索 → 构建 Prompt → LLM 生成 → 流式返回
    │          │          │               │           │          │
    │    Embedding    ChromaDB        检索结果+     Ollama    SSE
    │    模型(512维)  余弦相似度       对话历史    Qwen2:7b  实时输出
```

---

## 四、数据库设计

### 4.1 核心表结构

| 表名 | 说明 | 核心字段 |
|------|------|----------|
| **users** | 用户表 | id, username, email, password_hash, role, status, avatar |
| **documents** | 文件表 | id, owner_id, filename, description, file_type, is_public, version |
| **document_versions** | 文件版本历史 | id, document_id, version, file_path, file_size |
| **document_tags** | 文件-标签关联 | document_id, tag_id |
| **user_files** | 用户文件引用 | id, user_id, document_id, created_at |
| **conversations** | 对话表 | id, user_id, title, created_at |
| **messages** | 消息表 | id, conversation_id, role, content, sources |
| **feedbacks** | 反馈表 | id, user_id, message_id, rating, comment |
| **tags** | 标签表 | id, name, color |
| **settings** | 系统设置 | id, key, value |
| **audit_logs** | 审计日志 | id, user_id, action, resource, detail |

### 4.2 数据关系

```
users 1──N documents 1──N document_versions
  │          │
  │          └──N──N tags (通过 document_tags)
  │
  ├──1──N user_files N──1 documents (文件引用关系)
  │
  ├──1──N conversations 1──N messages
  │                    └──1──N feedbacks
  │
  └──1──N audit_logs
```

### 4.3 文件引用模式

```
用户A上传文件 → documents (owner_id = A)
    │
    └──用户B在知识广场添加引用 → user_files (user_id = B, document_id = 文件ID)
                                    │
                                    ├── B 可查看该文件
                                    ├── B 可删除引用（从列表移除）
                                    └── B 不可修改文件内容
```

---

## 五、安全设计

### 5.1 认证安全

| 安全措施 | 实现方式 |
|----------|----------|
| JWT 双 Token | Access Token (60分钟) + Refresh Token (7天) |
| Token 自动刷新 | Access Token 过期时自动使用 Refresh Token 续期 |
| Token 轮换 | Refresh Token 使用后立即失效，防止重放攻击 |
| 密码哈希 | PBKDF2 + 随机盐值，100,000 次迭代 |
| 时序攻击防护 | hmac.compare_digest() 常量时间比较 |
| 频率限制 | 基于 IP+用户名的登录频率限制（5分钟10次） |

### 5.2 数据安全

| 安全措施 | 实现方式 |
|----------|----------|
| XSS 防护 | DOMPurify 消毒所有 HTML 输出 |
| SQL 注入防护 | SQLAlchemy ORM 参数化查询 |
| 文件上传验证 | 前端+后端双重类型白名单 + 大小限制（50MB） |
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
python -m venv venv
venv\Scripts\activate  # Windows
pip install -r requirements.txt
cp .env.example .env
# 编辑 .env 文件，配置数据库密码
python scripts/seed_data.py
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
│   │   ├── api/               # API 路由层（auth, files, chat, tags, admin 等）
│   │   ├── core/              # 核心模块（数据库、安全、文档解析、分块）
│   │   ├── services/          # 业务逻辑层（document, chat, vector_store 等）
│   │   ├── models/            # 数据模型层（user, document, tag, user_file 等）
│   │   ├── schemas/           # Pydantic 数据模式
│   │   ├── middleware/         # 中间件（日志、异常处理）
│   │   └── main.py            # 应用入口
│   └── requirements.txt
│
├── user-web/                   # 用户端前端
│   └── src/
│       ├── views/             # 页面组件（11个页面）
│       ├── api/               # API 调用层
│       ├── stores/            # Pinia 状态管理（auth, theme）
│       ├── router/            # 路由配置（守卫、懒加载、动态标题）
│       ├── utils/             # 工具函数（formatFileSize, getFileTypeClass 等）
│       └── styles/            # 全局样式 + 深色模式
│
├── admin-web/                  # 管理端前端
│   └── src/
│       ├── views/             # 页面组件（7个页面）
│       ├── api/               # API 调用层
│       └── stores/            # 状态管理
│
├── ARCHITECTURE.md             # 系统架构文档
├── FEATURE_NOTES.md            # 功能实现笔记（含答辩准备）
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
| 认证 | POST /api/auth/refresh | Token 刷新 |
| 认证 | GET /api/auth/me | 获取当前用户 |
| 文件 | GET /api/files | 我的文件列表（支持筛选排序） |
| 文件 | POST /api/files/upload | 上传文件 |
| 文件 | GET /api/files/{id} | 文件详情 |
| 文件 | PUT /api/files/{id} | 更新文件信息 |
| 文件 | DELETE /api/files/{id} | 删除文件/引用 |
| 文件 | PUT /api/files/{id}/replace | 替换文件内容 |
| 文件 | GET /api/files/shared | 公开文件列表（知识广场） |
| 文件 | POST /api/files/{id}/add | 添加文件引用 |
| 聊天 | POST /api/chat | 发送消息（支持流式） |
| 对话 | GET /api/conversations | 对话列表 |
| 标签 | GET /api/tags | 标签列表 |

---

## 九、项目亮点

### 技术亮点
1. **RAG 检索增强生成**：基于向量检索的精准问答，BGE-small 中文 Embedding，跨文件检索
2. **流式响应架构**：SSE 实时输出 + 超时保护，用户体验流畅
3. **文件引用模式**：知识广场采用引用而非复制，节省存储空间，避免数据冗余
4. **Token 自动刷新**：Access Token 过期无感续期，用户体验连贯
5. **全站深色模式**：CSS 变量方案，所有页面完整适配
6. **本地化部署**：Ollama 本地 LLM + BGE Embedding，保护数据隐私

### 安全亮点
1. **JWT 双 Token 认证**：Access Token + Refresh Token 自动刷新轮换
2. **密码安全存储**：PBKDF2 + 盐值 + 常量时间比较
3. **频率限制**：基于 IP 的登录频率限制
4. **XSS 防护**：DOMPurify 消毒所有 HTML 输出

### UX 亮点
1. **多维度筛选排序**：文件格式、上传人、标签筛选 + 热度/时间/大小排序
2. **登录回跳**：被拦截后登录自动跳回目标页
3. **深色模式**：全局主题切换，平滑过渡动画
4. **表单验证**：编辑/上传/替换文件均有前端校验
5. **移动端适配**：聊天消息操作按钮在移动端始终可见

---

## 十、未来规划

### 短期（1-2周）
- [x] 文件引用模式（知识广场添加引用）
- [x] 多维度筛选排序
- [x] 深色模式
- [x] Token 自动刷新
- [ ] 文件描述 AI 自动生成
- [ ] 对话导出增强

### 中期（1-2月）
- [ ] 文件标签 AI 自动推荐
- [ ] 文件使用分析统计
- [ ] 多轮对话记忆优化

### 长期（3-6月）
- [ ] 协作功能
- [ ] 多模态支持
- [ ] API 开放平台

---

## 十一、相关文档

| 文档 | 说明 |
|------|------|
| [ARCHITECTURE.md](ARCHITECTURE.md) | 系统架构详解 |
| [FEATURE_NOTES.md](FEATURE_NOTES.md) | 功能实现笔记（含面试准备） |
| [PROJECT_STRUCTURE.md](PROJECT_STRUCTURE.md) | 项目结构详解 |
| [ROADMAP.md](ROADMAP.md) | 功能扩展规划 |
| [SETUP.md](SETUP.md) | 环境搭建指南 |
| [DEFENSE_PREP.md](DEFENSE_PREP.md) | 答辩准备材料 |
| [PPT_OUTLINE.md](PPT_OUTLINE.md) | PPT 大纲 |

---

## 十二、License

MIT

---

## 十三、联系方式

- **GitHub**: https://github.com/wy050601WLS/CogniQ
- **Issues**: https://github.com/wy050601WLS/CogniQ/issues

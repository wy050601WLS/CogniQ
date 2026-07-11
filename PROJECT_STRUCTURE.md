# 知识问答系统 - 项目结构详解

> 本文档详细标注了项目中每个文件的作用和职责。

---

## 一、项目根目录

```
knowledge-qa/
│
├── backend/                    # 后端 API 服务（Python + FastAPI）
├── user-web/                   # 用户端前端（Vue 3 + Element Plus）
├── admin-web/                  # 管理端前端（Vue 3 + Element Plus）
│
├── .git/                       # Git 版本控制
├── .gitignore                  # Git 忽略规则
│
├── README.md                   # 项目说明文档
├── SETUP.md                    # 环境搭建指南
├── ROADMAP.md                  # 项目开发路线图
├── ARCHITECTURE.md             # 系统架构文档
├── FEATURE_NOTES.md            # 功能实现笔记（含面试准备）
├── PPT_OUTLINE.md              # PPT 内容大纲
├── PROJECT_INTRODUCTION.md     # 项目介绍文档
└── 知识问答系统项目汇报.pptx      # 项目汇报 PPT
```

---

## 二、后端结构（backend/）

```
backend/
├── app/                        # 应用主目录
│   ├── __init__.py             # 包初始化文件
│   │
│   ├── main.py                 # 🚀 应用入口
│   │                           #   - FastAPI 应用创建
│   │                           #   - 中间件配置（CORS、日志、错误处理）
│   │                           #   - 路由挂载
│   │                           #   - 静态文件服务
│   │                           #   - 异常处理器注册
│   │                           #   - 健康检查端点
│   │
│   ├── config.py               # ⚙️ 配置管理
│   │                           #   - Pydantic Settings 读取 .env
│   │                           #   - 数据库连接配置
│   │                           #   - JWT 密钥配置
│   │                           #   - LLM/Embedding 模型配置
│   │                           #   - 文件上传配置
│   │
│   ├── exceptions.py           # ❌ 自定义异常体系
│   │                           #   - AppException 基类
│   │                           #   - NotFoundError (404)
│   │                           #   - ValidationError (422)
│   │                           #   - PermissionDeniedError (403)
│   │                           #   - UnauthorizedError (401)
│   │                           #   - BadRequestError (400)
│   │
│   ├── deps.py                 # 🔗 依赖注入
│   │                           #   - get_current_user() 获取当前用户
│   │                           #   - get_current_admin() 获取管理员
│   │
│   ├── api/                    # 🛣️ API 路由层
│   │   ├── __init__.py
│   │   ├── router.py           #   路由汇总，注册所有子路由
│   │   ├── auth.py             #   认证模块
│   │   │                         - POST /register 用户注册
│   │   │                         - POST /login 用户登录
│   │   │                         - POST /refresh 刷新 Token
│   │   │                         - GET /me 获取当前用户
│   │   │                         - PUT /me 更新个人信息
│   │   │                         - PUT /password 修改密码
│   │   │                         - POST /avatar 上传头像
│   │   ├── knowledge_base.py   #   知识库模块
│   │   │                         - GET /my 我的知识库
│   │   │                         - GET /marketplace 知识库广场
│   │   │                         - POST / 创建知识库
│   │   │                         - GET /{id} 知识库详情
│   │   │                         - PUT /{id} 更新知识库
│   │   │                         - DELETE /{id} 删除知识库
│   │   │                         - POST /{id}/copy 复制知识库
│   │   ├── document.py         #   文档模块
│   │   │                         - GET /knowledge-bases/{kb_id}/documents 文档列表
│   │   │                         - POST /knowledge-bases/{kb_id}/documents/upload 上传文档
│   │   │                         - GET /documents/{id} 文档详情
│   │   │                         - DELETE /documents/{id} 删除文档
│   │   ├── chat.py             #   聊天模块
│   │   │                         - GET /conversations 对话列表
│   │   │                         - POST /conversations 创建对话
│   │   │                         - GET /conversations/{id}/messages 消息历史
│   │   │                         - DELETE /conversations/{id} 删除对话
│   │   │                         - GET /conversations/search 搜索对话
│   │   │                         - GET /conversations/{id}/export 导出对话
│   │   │                         - POST /chat 发送消息（支持流式）
│   │   ├── settings.py         #   系统设置模块
│   │   │                         - GET / 获取设置
│   │   │                         - PUT / 更新设置
│   │   ├── favorites.py        #   收藏模块
│   │   │                         - GET / 收藏列表
│   │   │                         - POST / 添加收藏
│   │   │                         - DELETE /{id} 取消收藏
│   │   ├── feedback.py         #   反馈模块
│   │   │                         - POST / 提交反馈
│   │   ├── tags.py             #   标签模块
│   │   │                         - GET / 标签列表
│   │   │                         - POST / 创建标签
│   │   │                         - DELETE /{id} 删除标签
│   │   ├── help.py             #   帮助模块
│   │   │                         - GET /help 分类列表
│   │   │                         - GET /help/search 搜索帮助
│   │   │                         - GET /help/{id} 分类详情
│   │   │                         - GET /help/item/{id} 帮助项详情
│   │   └── admin.py            #   管理后台模块
│   │                             - GET /users 用户列表
│   │                             - PUT /users/{id} 更新用户
│   │                             - DELETE /users/{id} 删除用户
│   │                             - GET /knowledge-bases 知识库列表
│   │                             - DELETE /knowledge-bases/{id} 删除知识库
│   │                             - GET /documents 文档列表
│   │                             - DELETE /documents/{id} 删除文档
│   │                             - GET /stats/* 数据统计
│   │
│   ├── core/                   # 🔧 核心模块
│   │   ├── __init__.py
│   │   ├── database.py         #   数据库配置
│   │   │                         - SQLAlchemy 异步引擎
│   │   │                         - 连接池配置
│   │   │                         - async_session 会话工厂
│   │   │                         - get_db() 依赖注入
│   │   │                         - init_db() 初始化数据库
│   │   ├── security.py         #   安全模块
│   │   │                         - hash_password() 密码哈希
│   │   │                         - verify_password() 密码验证
│   │   │                         - create_access_token() 创建 Access Token
│   │   │                         - create_refresh_token() 创建 Refresh Token
│   │   │                         - decode_token() 解码 Token
│   │   ├── chunker.py          #   文本分块器
│   │   │                         - split_text() 使用 LangChain 分块
│   │   │                         - RecursiveCharacterTextSplitter
│   │   └── document_parser.py  #   文档解析器
│   │                             - parse_document() 多格式解析入口
│   │                             - parse_pdf() PDF 解析
│   │                             - parse_docx() Word 解析
│   │                             - parse_markdown() Markdown 解析
│   │                             - parse_text() 纯文本解析
│   │                             - parse_html() HTML 解析
│   │
│   ├── services/               # 💼 业务逻辑层
│   │   ├── __init__.py
│   │   ├── chat.py             #   RAG 问答服务（核心）
│   │   │                         - rag_chat() RAG 问答主函数
│   │   │                         - check_sensitive_content() 敏感词检查
│   │   │                         - filter_response() 输出过滤
│   │   │                         - format_history() 格式化对话历史
│   │   │                         - process_document() 文档处理
│   │   ├── chat_service.py     #   聊天业务逻辑
│   │   │                         - list_conversations() 对话列表
│   │   │                         - create_conversation() 创建对话
│   │   │                         - list_messages() 消息列表
│   │   │                         - delete_conversation() 删除对话
│   │   │                         - chat_stream() 流式聊天
│   │   │                         - chat_non_stream() 非流式聊天
│   │   ├── llm.py              #   LLM 服务
│   │   │                         - LLMService 类
│   │   │                         - stream_chat() 流式聊天
│   │   │                         - chat() 非流式聊天
│   │   │                         - list_models() 列出模型
│   │   ├── vector_store.py     #   向量存储服务
│   │   │                         - VectorStoreService 类
│   │   │                         - get_or_create_collection() 获取/创建集合
│   │   │                         - add_documents() 添加文档
│   │   │                         - query() 查询相似文档
│   │   │                         - delete_documents() 删除文档
│   │   ├── embeddings.py       #   Embedding 服务
│   │   │                         - EmbeddingService 类
│   │   │                         - embed_documents() 批量嵌入
│   │   │                         - embed_query() 单条嵌入
│   │   ├── knowledge_base.py   #   知识库业务逻辑
│   │   │                         - KnowledgeBaseService 类
│   │   │                         - list_by_owner() 用户知识库列表
│   │   │                         - list_public() 公开知识库列表
│   │   │                         - create() 创建知识库
│   │   │                         - update() 更新知识库
│   │   │                         - delete() 删除知识库
│   │   │                         - copy() 复制知识库
│   │   ├── document.py         #   文档业务逻辑
│   │   │                         - DocumentService 类
│   │   │                         - list_by_kb() 文档列表
│   │   │                         - upload_and_process() 上传并处理
│   │   │                         - delete() 删除文档
│   │   ├── settings.py         #   设置业务逻辑
│   │   │                         - SettingsService 类
│   │   │                         - get_settings() 获取设置
│   │   │                         - update_settings() 更新设置
│   │   └── audit_log.py        #   审计日志服务
│   │                             - log_action() 记录操作日志
│   │
│   ├── models/                 # 📊 数据模型层（SQLAlchemy ORM）
│   │   ├── __init__.py         #   模型汇总导入
│   │   ├── user.py             #   用户模型
│   │   │                         - id, username, email, password_hash
│   │   │                         - nickname, avatar, role, status
│   │   ├── knowledge_base.py   #   知识库模型
│   │   │                         - id, owner_id, name, description
│   │   │                         - is_public, is_official, allow_copy
│   │   │                         - chunk_size, chunk_overlap, doc_count
│   │   ├── document.py         #   文档模型
│   │   │                         - id, knowledge_base_id, filename
│   │   │                         - file_type, file_size, file_path
│   │   │                         - status, error_message, chunk_count
│   │   ├── conversation.py     #   对话模型
│   │   │                         - Conversation: id, user_id, knowledge_base_id, title
│   │   │                         - Message: id, conversation_id, role, content, sources
│   │   ├── feedback.py         #   反馈模型
│   │   │                         - id, user_id, message_id, conversation_id
│   │   │                         - rating, comment
│   │   ├── favorite.py         #   收藏模型
│   │   │                         - id, user_id, knowledge_base_id
│   │   │                         - UniqueConstraint(user_id, knowledge_base_id)
│   │   ├── tag.py              #   标签模型
│   │   │                         - id, name, color
│   │   ├── setting.py          #   设置模型
│   │   │                         - key, value, description
│   │   └── audit_log.py        #   审计日志模型
│   │                             - id, user_id, username, action
│   │                             - resource_type, resource_id, detail
│   │
│   ├── schemas/                # 📝 Pydantic 数据模式
│   │   ├── __init__.py
│   │   ├── auth.py             #   认证相关模式
│   │   │                         - RegisterRequest, LoginRequest
│   │   │                         - TokenResponse, RefreshTokenRequest
│   │   ├── user.py             #   用户相关模式
│   │   │                         - UserResponse, UserUpdateRequest
│   │   │                         - ChangePasswordRequest
│   │   ├── knowledge_base.py   #   知识库相关模式
│   │   │                         - KnowledgeBaseCreate, KnowledgeBaseUpdate
│   │   │                         - KnowledgeBaseResponse, KnowledgeBaseListResponse
│   │   ├── document.py         #   文档相关模式
│   │   │                         - DocumentResponse
│   │   ├── chat.py             #   聊天相关模式
│   │   │                         - ChatRequest, ChatResponse
│   │   │                         - ConversationCreate, ConversationResponse
│   │   │                         - MessageResponse
│   │   └── settings.py         #   设置相关模式
│   │                             - SettingsResponse
│   │                             - LLMSettings, EmbeddingSettings, ChunkingSettings
│   │
│   ├── middleware/              # 🔌 中间件
│   │   ├── __init__.py
│   │   ├── logging.py          #   请求日志中间件
│   │   │                         - 记录请求方法、路径、状态码、耗时
│   │   └── error_handler.py    #   全局错误处理中间件
│   │                             - 捕获未处理异常
│   │                             - 返回统一错误格式
│   │
│   ├── data/                   # 📁 数据目录
│   │   └── help_content.py     #   帮助内容数据（硬编码）
│   │                             - 7 个分类
│   │                             - 16 个帮助项
│   │
│   └── utils/                  # 🛠️ 工具函数
│       ├── __init__.py
│       └── helpers.py          #   通用辅助函数
│                                 - get_or_404() 获取对象或返回 404
│
├── requirements.txt            # 📦 Python 依赖列表
├── .env                        # 🔐 环境变量配置（不提交到 Git）
├── .env.example                # 📄 环境变量示例
│
└── scripts/                    # 📜 脚本目录
    └── seed_data.py            #   测试数据填充脚本
```

---

## 三、用户端前端结构（user-web/）

```
user-web/
├── src/                        # 源代码目录
│   ├── main.js                 # 🚀 应用入口
│   │                           #   - 创建 Vue 应用
│   │                           #   - 注册 Element Plus
│   │                           #   - 注册 Pinia
│   │                           #   - 注册路由器
│   │
│   ├── App.vue                 # 🏠 根组件
│   │                           #   - 侧边栏导航
│   │                           #   - 顶部栏（搜索、主题切换）
│   │                           #   - 页面内容区
│   │                           #   - 返回顶部按钮
│   │
│   ├── router/                 # 🛣️ 路由配置
│   │   └── index.js            #   路由定义
│   │                             - / 首页
│   │                             - /login 登录
│   │                             - /register 注册
│   │                             - /chat 智能问答
│   │                             - /my-kb 我的知识库
│   │                             - /kb/:id 知识库详情
│   │                             - /favorites 收藏
│   │                             - /history 对话历史
│   │                             - /profile 个人中心
│   │                             - /marketplace 知识库广场
│   │                             - /help 帮助中心
│   │                             - /:pathMatch(.*)* 404页面
│   │
│   ├── stores/                 # 📦 Pinia 状态管理
│   │   ├── auth.js             #   认证状态
│   │   │                         - token, user, isInitialized
│   │   │                         - doLogin(), doRegister(), logout()
│   │   │                         - fetchUser()
│   │   └── theme.js            #   主题状态
│   │                             - isDark 深色模式开关
│   │                             - toggle() 切换主题
│   │
│   ├── api/                    # 🌐 API 调用层
│   │   ├── index.js            #   Axios 实例配置
│   │   │                         - baseURL: /api
│   │   │                         - 请求拦截器（自动附加 Token）
│   │   │                         - 响应拦截器（401 跳转登录）
│   │   ├── auth.js             #   认证相关 API
│   │   │                         - login(), register(), getMe()
│   │   │                         - updateProfile(), changePassword()
│   │   │                         - uploadAvatar()
│   │   └── knowledgeBase.js    #   知识库相关 API
│   │                             - getMarketplace(), getMyKnowledgeBases()
│   │                             - createKnowledgeBase(), deleteKnowledgeBase()
│   │                             - getDocuments(), uploadDocument()
│   │                             - getConversations(), createConversation()
│   │                             - chatStream() 流式聊天
│   │                             - getFavorites(), addFavorite()
│   │                             - submitFeedback()
│   │
│   ├── views/                  # 📄 页面组件
│   │   ├── Home.vue            #   首页
│   │   │                         - 统计概览
│   │   │                         - 推荐知识库
│   │   │                         - 快捷操作入口
│   │   ├── Login.vue           #   登录页
│   │   ├── Register.vue        #   注册页
│   │   ├── Chat.vue            #   智能问答页（核心）
│   │   │                         - 左侧对话列表
│   │   │                         - 知识库选择
│   │   │                         - 消息展示（支持 Markdown）
│   │   │                         - 流式输入框
│   │   │                         - 来源引用展示
│   │   ├── MyKnowledgeBases.vue #  我的知识库页
│   │   │                         - 知识库列表
│   │   │                         - 创建知识库弹窗
│   │   ├── KnowledgeBaseDetail.vue # 知识库详情页
│   │   │                         - 文档列表
│   │   │                         - 文档上传
│   │   │                         - 文档删除
│   │   ├── Marketplace.vue     #   知识库广场页
│   │   │                         - 公开知识库列表
│   │   │                         - 搜索筛选
│   │   │                         - 复制知识库
│   │   ├── Favorites.vue       #   收藏页
│   │   │                         - 收藏列表
│   │   │                         - 取消收藏
│   │   ├── History.vue         #   对话历史页
│   │   │                         - 对话列表
│   │   │                         - 搜索对话
│   │   │                         - 删除对话
│   │   ├── Profile.vue         #   个人中心页
│   │   │                         - 头像上传
│   │   │                         - 个人信息修改
│   │   │                         - 密码修改
│   │   ├── Help.vue            #   帮助中心页
│   │   │                         - 分类卡片
│   │   │                         - 搜索帮助
│   │   │                         - 详情弹窗
│   │   └── NotFound.vue        #   404 页面
│   │
│   └── styles/                 # 🎨 样式文件
│       └── global.css          #   全局样式
│                                 - 深色模式变量
│                                 - 通用样式重置
│
├── public/                     # 📁 静态资源
│   └── index.html              #   HTML 入口
│
├── index.html                  #   Vite HTML 入口
├── vite.config.js              # ⚙️ Vite 配置
│                                 - 开发服务器端口 5175
│                                 - API 代理配置
├── package.json                # 📦 依赖配置
└── .env                        # 🔐 环境变量
```

---

## 四、管理端前端结构（admin-web/）

```
admin-web/
├── src/                        # 源代码目录
│   ├── main.js                 # 🚀 应用入口
│   │
│   ├── App.vue                 # 🏠 根组件
│   │                           #   - 可折叠侧边栏
│   │                           #   - 顶部栏
│   │                           #   - 页面内容区
│   │
│   ├── router/                 # 🛣️ 路由配置
│   │   └── index.js            #   路由定义
│   │                             - /login 登录
│   │                             - /dashboard 仪表盘
│   │                             - /users 用户管理
│   │                             - /knowledge-bases 知识库管理
│   │                             - /documents 文档管理
│   │                             - /statistics 数据统计
│   │                             - /settings 系统设置
│   │                             - /:pathMatch(.*)* 404页面
│   │
│   ├── stores/                 # 📦 Pinia 状态管理
│   │   ├── auth.js             #   管理员认证状态
│   │   │                         - admin_token, admin_user
│   │   │                         - doLogin(), logout()
│   │   └── theme.js            #   主题状态
│   │
│   ├── api/                    # 🌐 API 调用层
│   │   └── index.js            #   Axios 实例 + 所有 API
│   │                             - login()
│   │                             - getUsers(), updateUser(), deleteUser()
│   │                             - getAdminKnowledgeBases()
│   │                             - getAdminDocuments()
│   │                             - getOverviewStats(), getUserStats(), getTrends()
│   │                             - getAdminSettings(), updateAdminSettings()
│   │
│   ├── views/                  # 📄 页面组件
│   │   ├── Login.vue           #   管理员登录页
│   │   ├── Dashboard.vue       #   仪表盘
│   │   │                         - 数据概览卡片
│   │   │                         - 快捷操作入口
│   │   ├── Users.vue           #   用户管理页
│   │   │                         - 用户列表表格
│   │   │                         - 禁用/启用用户
│   │   │                         - 删除用户
│   │   ├── KnowledgeBases.vue  #   知识库管理页
│   │   │                         - 知识库列表表格
│   │   │                         - 删除知识库
│   │   ├── Documents.vue       #   文档管理页
│   │   │                         - 文档列表表格
│   │   │                         - 状态筛选
│   │   │                         - 删除文档
│   │   ├── Statistics.vue      #   数据统计页
│   │   │                         - 用户增长趋势
│   │   │                         - 对话使用趋势
│   │   ├── Settings.vue        #   系统设置页
│   │   │                         - LLM 配置
│   │   │                         - 嵌入模型配置
│   │   │                         - 分块参数配置
│   │   └── NotFound.vue        #   404 页面
│   │
│   └── styles/                 # 🎨 样式文件
│       └── global.css          #   全局样式
│
├── public/                     # 📁 静态资源
│   └── index.html
│
├── index.html
├── vite.config.js              # ⚙️ Vite 配置（端口 5174）
├── package.json
└── .env
```

---

## 五、核心文件说明

### 5.1 后端核心文件

| 文件 | 作用 | 代码行数 |
|------|------|----------|
| `main.py` | 应用入口，配置中间件和路由 | ~120 |
| `config.py` | 配置管理，读取环境变量 | ~65 |
| `security.py` | JWT 和密码安全 | ~60 |
| `database.py` | 数据库连接配置 | ~35 |
| `chat.py` (services) | RAG 问答核心逻辑 | ~220 |
| `vector_store.py` | ChromaDB 向量存储 | ~95 |
| `llm.py` | Ollama LLM 服务封装 | ~75 |
| `chat_service.py` | 聊天业务逻辑 | ~300 |
| `knowledge_base.py` (services) | 知识库业务逻辑 | ~175 |
| `document.py` (services) | 文档处理业务逻辑 | ~170 |

### 5.2 前端核心文件

| 文件 | 作用 | 代码行数 |
|------|------|----------|
| `Chat.vue` | 智能问答页面（核心） | ~680 |
| `App.vue` (user-web) | 用户端根组件 | ~500 |
| `App.vue` (admin-web) | 管理端根组件 | ~200 |
| `knowledgeBase.js` | API 调用层 | ~110 |
| `auth.js` (stores) | 认证状态管理 | ~60 |

---

## 六、配置文件说明

| 文件 | 作用 |
|------|------|
| `.env` | 环境变量（数据库、JWT、LLM 等） |
| `.gitignore` | Git 忽略规则 |
| `vite.config.js` | Vite 构建配置 |
| `package.json` | npm 依赖配置 |
| `requirements.txt` | Python 依赖列表 |

---

## 七、数据流向

```
用户操作
    │
    ▼
┌─────────────────────────────────────────┐
│  前端 (Vue 3)                           │
│  - 用户交互                             │
│  - 状态管理 (Pinia)                     │
│  - API 调用 (Axios)                     │
└─────────────────────────────────────────┘
    │
    │ HTTP/SSE 请求
    ▼
┌─────────────────────────────────────────┐
│  后端 (FastAPI)                         │
│  - 路由层 (api/)                        │
│  - 业务逻辑层 (services/)               │
│  - 数据模型层 (models/)                 │
│  - 核心模块 (core/)                     │
└─────────────────────────────────────────┘
    │
    │ SQL/向量查询
    ▼
┌─────────────────────────────────────────┐
│  数据层                                 │
│  - MySQL (关系数据)                     │
│  - ChromaDB (向量数据)                  │
│  - Ollama (LLM 服务)                    │
└─────────────────────────────────────────┘
```

---

## 八、技术栈汇总

| 层级 | 技术 | 文件位置 |
|------|------|----------|
| **后端框架** | FastAPI | `backend/app/main.py` |
| **ORM** | SQLAlchemy | `backend/app/core/database.py` |
| **数据库** | MySQL | `backend/.env` |
| **向量库** | ChromaDB | `backend/app/services/vector_store.py` |
| **LLM** | Ollama | `backend/app/services/llm.py` |
| **Embedding** | sentence-transformers | `backend/app/services/embeddings.py` |
| **文本分块** | LangChain | `backend/app/core/chunker.py` |
| **前端框架** | Vue 3 | `user-web/src/main.js` |
| **UI 组件** | Element Plus | `user-web/src/views/*.vue` |
| **状态管理** | Pinia | `user-web/src/stores/` |
| **路由** | Vue Router | `user-web/src/router/` |
| **HTTP 客户端** | Axios | `user-web/src/api/index.js` |
| **构建工具** | Vite | `user-web/vite.config.js` |

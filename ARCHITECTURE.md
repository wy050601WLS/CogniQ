# 知识问答系统 - 功能架构与技术栈文档

## 一、项目概述

**知识问答系统（Knowledge QA）** 是一个基于 RAG（检索增强生成）技术的智能知识问答平台。用户可以上传文档到知识库，系统会自动解析、分块、向量化并存储，然后通过 AI 模型对用户的问题进行检索增强生成回答。

### 核心价值
- **知识管理**：支持多种格式文档的上传、解析和管理
- **智能问答**：基于 RAG 技术，AI 可以根据知识库内容精准回答问题
- **来源引用**：每个回答都标注参考来源，确保可追溯性
- **多轮对话**：支持上下文记忆，理解用户追问

---

## 二、核心功能模块

### 2.1 用户认证模块

#### 功能实现
- **注册**：用户名、邮箱、密码注册，自动登录
- **登录**：支持用户名或邮箱登录，JWT Token 签发
- **Token 刷新**：Access Token 过期后使用 Refresh Token 刷新
- **密码修改**：验证旧密码后修改

#### 核心技术：JWT（JSON Web Token）

**是什么？**
JWT 是一种开放标准（RFC 7519），用于在各方之间安全地传输信息。它由三部分组成：Header（头部）、Payload（负载）、Signature（签名），用 `.` 连接。

**为什么用？**
- **无状态**：服务器不需要存储会话信息，适合分布式系统
- **跨域支持**：Token 可在不同域名间传递
- **安全性**：签名机制防止篡改

**如何使用？**
```python
# 创建 Token
from jose import jwt
token = jwt.encode({"sub": user_id, "exp": expire}, secret_key, algorithm="HS256")

# 验证 Token
payload = jwt.decode(token, secret_key, algorithms=["HS256"])
```

#### 安全机制
- **频率限制**：基于 IP 的登录/注册频率限制，防止暴力破解
- **Token 轮换**：Refresh Token 使用后立即失效，防止重放攻击
- **密码哈希**：使用 PBKDF2 算法 + 盐值存储密码

---

### 2.2 知识库管理模块

#### 功能实现
- **创建知识库**：设置名称、描述、可见性（公开/私有）
- **编辑知识库**：修改基本信息
- **删除知识库**：级联删除文档和向量数据
- **复制知识库**：复制公开知识库的元数据和文档记录
- **知识库广场**：浏览和搜索公开知识库

#### 核心技术：关系型数据库 + ORM

**是什么？**
- **MySQL**：开源关系型数据库，支持 ACID 事务
- **SQLAlchemy**：Python 的 ORM（对象关系映射）框架

**为什么用？**
- **数据一致性**：事务支持确保数据完整性
- **查询灵活**：支持复杂查询和关联
- **ORM 便捷**：用 Python 对象操作数据库，避免手写 SQL

**如何使用？**
```python
# 定义模型
class KnowledgeBase(Base):
    __tablename__ = "knowledge_bases"
    id = Column(String(36), primary_key=True)
    name = Column(String(255), nullable=False)

# 查询
result = await db.execute(select(KnowledgeBase).where(KnowledgeBase.owner_id == user_id))
kbs = result.scalars().all()
```

---

### 2.3 文档处理模块

#### 功能实现
- **文档上传**：支持 PDF、Word、Markdown、TXT、HTML
- **文档解析**：提取文本内容
- **文本分块**：将长文本分割为合适大小的块
- **向量化**：将文本转换为向量表示
- **状态管理**：processing → completed / error

#### 核心技术：文档解析 + 文本分块

**是什么？**
- **文档解析**：从 PDF、Word 等格式中提取纯文本
- **文本分块**：将长文本按语义或固定长度分割

**为什么用？**
- **LLM 限制**：大模型有上下文窗口限制，需要分块处理
- **检索精度**：小块文本检索更精准
- **避免截断**：确保完整语义单元不被切断

**如何使用？**
```python
# 文本分块
def split_text(text: str, chunk_size: int = 500, chunk_overlap: int = 50):
    chunks = []
    start = 0
    while start < len(text):
        end = start + chunk_size
        chunks.append(text[start:end])
        start = end - chunk_overlap  # 重叠部分
    return chunks
```

---

### 2.4 向量存储模块

#### 功能实现
- **向量存储**：将文档向量存入 ChromaDB
- **相似度检索**：根据问题向量检索相关文档
- **元数据过滤**：按知识库 ID 过滤
- **删除管理**：按文档 ID 删除向量数据

#### 核心技术：ChromaDB（向量数据库）

**是什么？**
ChromaDB 是一个开源的向量数据库，专门用于存储和检索高维向量。它支持相似度搜索，是 RAG 系统的核心组件。

**为什么用？**
- **高效检索**：基于 HNSW 算法，百万级数据毫秒级响应
- **持久化**：支持本地文件存储
- **简单易用**：Python API 友好

**如何使用？**
```python
import chromadb

# 创建客户端
client = chromadb.PersistentClient(path="./data/chroma")

# 创建集合
collection = client.get_or_create_collection(
    name="kb_123",
    metadata={"hnsw:space": "cosine"}
)

# 添加文档
collection.add(
    documents=["文本1", "文本2"],
    metadatas=[{"doc_id": "doc1"}, {"doc_id": "doc2"}],
    ids=["id1", "id2"]
)

# 查询
results = collection.query(query_texts=["问题"], n_results=5)
```

---

### 2.5 智能问答模块

#### 功能实现
- **RAG 问答**：检索相关文档 + 生成回答
- **流式响应**：SSE（Server-Sent Events）实时返回
- **来源引用**：标注参考来源和相似度分数
- **多轮对话**：支持上下文记忆
- **敏感词过滤**：检测不当内容

#### 核心技术：RAG（检索增强生成）

**是什么？**
RAG 是一种结合检索（Retrieval）和生成（Generation）的 AI 技术。系统先从知识库中检索相关文档，然后将这些文档作为上下文提供给大语言模型，生成更准确的回答。

**为什么用？**
- **减少幻觉**：基于真实文档回答，减少编造
- **知识更新**：无需重新训练模型，更新文档即可
- **来源可追溯**：每个回答都有参考来源

**如何使用？**
```
用户问题 → 向量化 → 检索相关文档 → 构建 Prompt → LLM 生成回答
```

#### 流式响应实现
```python
# 后端：SSE 生成器
async def chat_stream(data, db, user_id):
    yield f"data: {json.dumps({'type': 'start'})}\n\n"
    async for chunk, sources in rag_chat(kb_id, question, history):
        yield f"data: {json.dumps({'type': 'chunk', 'content': chunk})}\n\n"
    yield f"data: {json.dumps({'type': 'end'})}\n\n"

# 前端：ReadableStream 解析
const reader = response.body.getReader()
while (true) {
    const { done, value } = await reader.read()
    if (done) break
    // 解析 SSE 数据
}
```

---

### 2.6 LLM 服务模块

#### 功能实现
- **Ollama 集成**：本地部署大语言模型
- **流式聊天**：异步流式返回
- **超时控制**：120 秒超时
- **错误处理**：友好错误消息

#### 核心技术：Ollama（本地 LLM 运行时）

**是什么？**
Ollama 是一个轻量级的本地大语言模型运行时，支持在个人电脑上运行开源模型（如 Llama、Qwen 等）。

**为什么用？**
- **隐私保护**：数据不离开本地
- **零成本**：无需 API 费用
- **离线可用**：无需网络连接

**如何使用？**
```python
import ollama

# 异步客户端
client = ollama.AsyncClient(host="http://localhost:11434")

# 流式聊天
stream = await client.chat(
    model="qwen2:7b",
    messages=[{"role": "user", "content": prompt}],
    stream=True
)
async for chunk in stream:
    yield chunk["message"]["content"]
```

---

### 2.7 前端交互模块

#### 功能实现
- **路由管理**：Vue Router 实现页面路由
- **状态管理**：Pinia 管理认证状态
- **UI 组件**：Element Plus 组件库
- **Markdown 渲染**：marked + DOMPurify

#### 核心技术栈

**Vue 3**
- **是什么**：渐进式 JavaScript 框架
- **为什么用**：响应式数据、组件化、Composition API
- **如何使用**：`<script setup>` + `ref()` + `computed()`

**Pinia**
- **是什么**：Vue 的状态管理库
- **为什么用**：替代 Vuex，更简洁的 API
- **如何使用**：
```javascript
export const useAuthStore = defineStore('auth', () => {
  const token = ref('')
  const user = ref(null)
  function logout() { token.value = '' }
  return { token, user, logout }
})
```

**Element Plus**
- **是什么**：基于 Vue 3 的 UI 组件库
- **为什么用**：提供丰富的预设组件，加速开发
- **如何使用**：`<el-button>`、`<el-table>`、`<el-dialog>` 等

---

### 2.8 管理后台模块

#### 功能实现
- **用户管理**：查看、禁用、删除用户
- **知识库管理**：查看和删除所有知识库
- **文档管理**：查看和删除所有文档
- **数据统计**：用户增长和对话趋势
- **系统设置**：配置 LLM、嵌入模型等参数

#### 权限控制
```python
# 依赖注入验证管理员权限
async def get_current_admin(current_user: User = Depends(get_current_user)):
    if current_user.role != "admin":
        raise PermissionDeniedError("需要管理员权限")
    return current_user
```

---

## 三、系统架构

### 3.1 整体架构

```
┌─────────────────────────────────────────────────────────┐
│                      前端层                              │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐  │
│  │  用户端      │  │  管理端      │  │              │  │
│  │  (5175)      │  │  (5174)      │  │              │  │
│  └──────────────┘  └──────────────┘  └──────────────┘  │
└─────────────────────────────────────────────────────────┘
                           │
                           ▼
┌─────────────────────────────────────────────────────────┐
│                      API 网关                            │
│                 FastAPI (端口 8000)                      │
│  ┌──────────────────────────────────────────────────┐  │
│  │  认证 │ 知识库 │ 文档 │ 聊天 │ 设置 │ 管理后台   │  │
│  └──────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────┘
                           │
          ┌────────────────┼────────────────┐
          ▼                ▼                ▼
┌──────────────┐  ┌──────────────┐  ┌──────────────┐
│   MySQL      │  │  ChromaDB    │  │   Ollama     │
│  (关系数据)  │  │  (向量数据)  │  │  (LLM 服务)  │
└──────────────┘  └──────────────┘  └──────────────┘
```

### 3.2 数据流

```
用户提问
    │
    ▼
┌─────────────────┐
│ 1. 问题向量化    │  ← Embedding 模型
└─────────────────┘
    │
    ▼
┌─────────────────┐
│ 2. 向量检索      │  ← ChromaDB
│   (Top-K 相似)  │
└─────────────────┘
    │
    ▼
┌─────────────────┐
│ 3. 构建 Prompt   │  ← 检索结果 + 对话历史
└─────────────────┘
    │
    ▼
┌─────────────────┐
│ 4. LLM 生成      │  ← Ollama (Qwen2)
└─────────────────┘
    │
    ▼
┌─────────────────┐
│ 5. 流式返回      │  ← SSE
└─────────────────┘
```

---

## 四、数据库设计

### 4.1 核心表结构

| 表名 | 说明 | 核心字段 |
|------|------|----------|
| users | 用户表 | id, username, email, password_hash, role, status |
| knowledge_bases | 知识库表 | id, owner_id, name, is_public, chunk_size |
| documents | 文档表 | id, knowledge_base_id, filename, status, file_path |
| conversations | 对话表 | id, user_id, knowledge_base_id, title |
| messages | 消息表 | id, conversation_id, role, content, sources |
| feedbacks | 反馈表 | id, user_id, message_id, rating, comment |
| favorites | 收藏表 | id, user_id, knowledge_base_id |

### 4.2 关系图

```
users 1──N knowledge_bases 1──N documents
  │
  └──1──N conversations 1──N messages
                │
                └──1──N feedbacks
                
users 1──N favorites N──1 knowledge_bases
```

---

## 五、API 设计

### 5.1 路由结构

```
/api
├── /auth              # 认证
│   ├── POST /register
│   ├── POST /login
│   ├── POST /refresh
│   ├── GET /me
│   ├── PUT /me
│   ├── PUT /password
│   └── POST /avatar
├── /knowledge-bases   # 知识库
│   ├── GET /my
│   ├── GET /marketplace
│   ├── POST /
│   ├── GET /{id}
│   ├── PUT /{id}
│   ├── DELETE /{id}
│   └── POST /{id}/copy
├── /chat              # 聊天
│   ├── GET /conversations
│   ├── POST /conversations
│   ├── GET /conversations/{id}/messages
│   ├── DELETE /conversations/{id}
│   └── POST /chat
├── /settings          # 设置
│   ├── GET /
│   └── PUT /
└── /admin             # 管理后台
    ├── /users
    ├── /knowledge-bases
    ├── /documents
    └── /stats
```

### 5.2 统一响应格式

```json
{
  "code": 200,
  "message": "success",
  "data": {}
}
```

错误响应：
```json
{
  "error": {
    "code": "VALIDATION_ERROR",
    "message": "数据验证失败",
    "detail": {}
  }
}
```

---

## 六、安全设计

### 6.1 认证安全
- JWT Token 签发与验证
- Refresh Token 轮换机制
- 密码 PBKDF2 哈希 + 盐值
- 登录/注册频率限制

### 6.2 数据安全
- XSS 防护：DOMPurify 消毒 HTML
- SQL 注入防护：SQLAlchemy ORM
- 文件上传验证：类型、大小限制
- CORS 配置：限制跨域来源

### 6.3 运行时安全
- 生产环境禁用 Swagger UI
- JWT 密钥强制配置检查
- 错误信息脱敏
- 日志审计

---

## 七、性能优化

### 7.1 数据库优化
- 连接池配置（pool_size=5, max_overflow=10）
- 查询分页支持
- 索引优化

### 7.2 缓存策略
- 知识库列表缓存
- 设置项单次查询

### 7.3 异步处理
- 文档处理使用线程池
- LLM 调用超时控制
- 流式响应减少延迟

---

## 八、部署方案

### 8.1 开发环境
```bash
# 后端
cd backend && uvicorn app.main:app --reload

# 用户端
cd user-web && npm run dev

# 管理端
cd admin-web && npm run dev
```

### 8.2 生产环境
- 后端：Gunicorn + Uvicorn workers
- 前端：Nginx 静态文件服务
- 数据库：MySQL 8.0
- 向量库：ChromaDB 持久化
- LLM：Ollama 服务

---

## 九、技术选型对比

| 技术 | 选型 | 备选方案 | 选择理由 |
|------|------|----------|----------|
| Web 框架 | FastAPI | Django, Flask | 异步支持、自动文档、性能 |
| ORM | SQLAlchemy | Tortoise ORM | 成熟稳定、社区活跃 |
| 数据库 | MySQL | PostgreSQL, SQLite | 生态完善、运维简单 |
| 向量库 | ChromaDB | Milvus, Pinecone | 轻量级、本地部署 |
| LLM | Ollama | OpenAI API | 隐私保护、零成本 |
| 前端框架 | Vue 3 | React, Angular | 学习曲线平缓、中文生态 |
| UI 组件 | Element Plus | Ant Design Vue | 组件丰富、文档完善 |
| 状态管理 | Pinia | Vuex | 更简洁的 API |

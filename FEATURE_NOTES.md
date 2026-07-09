# 知识问答系统 - 功能实现笔记

> 本文档基于代码审查结果整理，涵盖核心功能实现、技术栈、重难点、答辩话术、简历编写和面试准备。

---

## 目录

- [模块一：RAG 智能问答（核心亮点）](#模块一rag-智能问答核心亮点)
- [模块二：文档处理与向量存储](#模块二文档处理与向量存储)
- [模块三：流式聊天 SSE](#模块三流式聊天-sse)
- [模块四：JWT 认证体系](#模块四jwt-认证体系)
- [模块五：知识库管理](#模块五知识库管理)
- [项目答辩话术](#项目答辩话术)
- [简历编写指南](#简历编写指南)
- [面试话术与高频问题](#面试话术与高频问题)

---

## 模块一：RAG 智能问答（核心亮点）

### 1.1 核心技术栈

#### RAG（Retrieval-Augmented Generation，检索增强生成）

**是什么？**
RAG 是一种结合「检索」和「生成」的 AI 技术架构。系统先从知识库中检索与用户问题相关的文档片段，然后将这些片段作为上下文提供给大语言模型（LLM），生成更准确、有据可依的回答。

**为什么用？**
- **减少幻觉**：LLM 可能编造信息，RAG 基于真实文档回答，大幅降低幻觉率
- **知识可更新**：无需重新训练模型，上传新文档即可更新知识库
- **来源可追溯**：每个回答都标注参考来源，用户可以验证
- **成本低**：相比微调模型，RAG 只需存储文档向量，成本极低

**如何使用？**
```
用户问题 → 向量化 → 检索 Top-K 相关文档 → 构建 Prompt → LLM 生成回答
```

#### Embedding 模型（BAAI/bge-small-zh-v1.5）

**是什么？**
Embedding 模型是将文本转换为高维向量（稠密向量）的模型。BAAI/bge-small-zh-v1.5 是北京智源人工智能研究院（BAAI）开发的中文文本嵌入模型，输出 512 维向量。

**为什么用？**
- **中文优化**：专门为中文场景训练，语义理解准确
- **轻量高效**：模型大小仅 100MB，推理速度快
- **本地部署**：使用 sentence-transformers 库，无需 API 调用
- **开源免费**：无商业限制

**如何使用？**
```python
from sentence_transformers import SentenceTransformer

model = SentenceTransformer("BAAI/bge-small-zh-v1.5")
embedding = model.encode(["你好世界"])  # 输出 512 维向量
```

#### ChromaDB（向量数据库）

**是什么？**
ChromaDB 是一个开源的向量数据库，专门用于存储和检索高维向量（Embedding）。它基于 HNSW（Hierarchical Navigable Small World）算法实现高效的近似最近邻搜索。

**为什么用？**
- **高效检索**：百万级向量毫秒级响应
- **持久化存储**：支持本地文件持久化
- **简单易用**：Python API 友好，几行代码即可使用
- **免费开源**：无商业限制

**如何使用？**
```python
# 创建集合（每个知识库一个集合）
collection = client.get_or_create_collection(
    name="kb_123",
    metadata={"hnsw:space": "cosine"}  # 使用余弦相似度
)

# 添加文档向量
collection.add(
    documents=["文本内容"],
    metadatas=[{"doc_id": "doc1"}],
    ids=["vector_id_1"]
)

# 查询相似文档
results = collection.query(
    query_texts=["用户问题"],
    n_results=5  # 返回最相关的5条
)
```

#### Ollama（本地 LLM 运行时）

**是什么？**
Ollama 是一个轻量级的本地大语言模型运行时，支持在个人电脑上运行开源模型（如 Qwen、Llama 等）。

**为什么用？**
- **隐私保护**：数据不离开本地，无需调用外部 API
- **零成本**：无需 API 费用
- **离线可用**：无需网络连接
- **易于部署**：一条命令即可运行模型

**如何使用？**
```bash
# 安装并运行模型
ollama pull qwen2:7b
ollama serve
```

```python
# Python 调用
import ollama
client = ollama.AsyncClient(host="http://localhost:11434")
stream = await client.chat(model="qwen2:7b", messages=[...], stream=True)
```

### 1.2 核心实现流程

```
┌─────────────────────────────────────────────────────────────────┐
│                        RAG 问答完整流程                          │
└─────────────────────────────────────────────────────────────────┘

用户输入问题
    │
    ▼
┌─────────────────┐
│ 1. 敏感词检查    │  ← check_sensitive_content()
│   (正则匹配)    │     防止恶意输入
└─────────────────┘
    │
    ▼
┌─────────────────┐
│ 2. 格式化历史    │  ← format_history()
│   (最近5轮)     │     支持多轮对话上下文
└─────────────────┘
    │
    ▼
┌─────────────────┐
│ 3. 向量检索      │  ← vector_store.query()
│   (ChromaDB)    │     返回 Top-5 相关文档
│   (余弦相似度)   │
└─────────────────┘
    │
    ▼
┌─────────────────┐
│ 4. 相似度过滤    │  ← score >= 0.3
│   (阈值过滤)    │     过滤不相关结果
└─────────────────┘
    │
    ├── 无相关文档 ──→ 使用 NO_CONTEXT_PROMPT
    │
    ▼
┌─────────────────┐
│ 5. 构建 Prompt   │  ← RAG_PROMPT_TEMPLATE
│   (上下文+历史)  │     注入检索结果和对话历史
└─────────────────┘
    │
    ▼
┌─────────────────┐
│ 6. LLM 生成      │  ← llm.stream_chat()
│   (流式输出)    │     Ollama 异步调用
└─────────────────┘
    │
    ▼
┌─────────────────┐
│ 7. 敏感词过滤    │  ← filter_response()
│   (输出过滤)    │     确保输出安全
└─────────────────┘
    │
    ▼
返回给用户（附带来源引用）
```

### 1.3 关键代码

**RAG 问答核心函数** (`backend/app/services/chat.py`)
```python
async def rag_chat(kb_id: str, question: str, history: list[dict] = None):
    # 1. 敏感词检查
    is_safe, msg = check_sensitive_content(question)
    if not is_safe:
        yield "您的问题包含不当内容，无法回答。", []
        return

    # 2. 格式化对话历史
    history_text = format_history(history or [])

    # 3. 向量检索（使用线程池避免阻塞）
    results = await asyncio.to_thread(vector_store.query, kb_id, question, 5)

    # 4. 过滤低相关性结果
    sources = []
    context_parts = []
    for i, doc in enumerate(results):
        if doc["score"] >= similarity_threshold:
            context_parts.append(f"[来源{i+1}] {doc['content']}")
            sources.append({...})

    # 5. 构建 Prompt 并流式生成
    prompt = RAG_PROMPT_TEMPLATE.format(
        context=context, history=history_text, question=question
    )
    async for chunk in llm.stream_chat(prompt):
        yield filter_response(chunk), sources
```

### 1.4 重难点与解决方案

#### 难点 1：向量检索与事件循环冲突

**问题**：ChromaDB 的查询是同步操作，在 FastAPI 的异步事件循环中调用会阻塞整个事件循环，导致其他请求无法处理。

**解决方案**：使用 `asyncio.to_thread()` 将同步操作放到线程池中执行。
```python
# ❌ 错误：阻塞事件循环
results = vector_store.query(kb_id, question, 5)

# ✅ 正确：使用线程池
results = await asyncio.to_thread(vector_store.query, kb_id, question, 5)
```

#### 难点 2：相似度阈值选择

**问题**：阈值太高会漏掉相关文档，太低会引入噪声。

**解决方案**：
- 默认阈值 0.3（余弦相似度），可通过配置调整
- 返回 Top-5 结果，由阈值过滤后再使用
- 实际效果通过测试验证调优

#### 难点 3：多轮对话上下文管理

**问题**：LLM 上下文窗口有限，不能把所有历史都传入。

**解决方案**：
- 只保留最近 5 轮对话（10 条消息）
- 每条消息截断到 500 字符
- 历史消息格式化为"用户：xxx\n助手：xxx"

---

## 模块二：文档处理与向量存储

### 2.1 核心技术栈

#### 文档解析

**是什么？**
从 PDF、Word、Markdown、TXT、HTML 等格式中提取纯文本内容。

**为什么用？**
- 不同格式文档需要统一处理
- 提取纯文本后才能进行分块和向量化

**如何使用？**
```python
# 策略模式：根据文件类型选择解析器
parsers = {
    '.pdf': parse_pdf,      # pypdf
    '.docx': parse_docx,    # python-docx
    '.md': parse_markdown,  # 直接读取
    '.txt': parse_text,     # 直接读取
    '.html': parse_html,    # BeautifulSoup
}
```

#### 文本分块（Chunking）— LangChain TextSplitter

**是什么？**
LangChain 是一个用于构建 LLM 应用的框架，其 TextSplitter 模块提供了多种文本分块策略。`RecursiveCharacterTextSplitter` 是其中最常用的分块器，按优先级递归分割文本。

**为什么用？**
- **语义保持**：按段落、句子、词的优先级分割，避免切断完整语义
- **可配置**：支持自定义分块大小和重叠字符数
- **成熟稳定**：LangChain 是 LLM 应用开发的事实标准

**如何使用？**
```python
from langchain_text_splitters import RecursiveCharacterTextSplitter

splitter = RecursiveCharacterTextSplitter(
    chunk_size=500,        # 每块最大500字符
    chunk_overlap=50,      # 块间重叠50字符
    separators=["\n\n", "\n", "。", "！", "？", " "]
)
chunks = splitter.split_text(text)
```

#### 文本分块（Chunking）

**是什么？**
将长文本分割成固定大小的块（chunk），每个块独立向量化和存储。

**为什么用？**
- LLM 上下文窗口有限，不能处理过长文本
- 小块文本检索更精准
- 分块重叠确保语义完整性

**如何使用？**
```python
from langchain_text_splitters import RecursiveCharacterTextSplitter

splitter = RecursiveCharacterTextSplitter(
    chunk_size=500,        # 每块最大500字符
    chunk_overlap=50,      # 块间重叠50字符
    separators=["\n\n", "\n", "。", "！", "？", " "]
)
chunks = splitter.split_text(text)
```

### 2.2 核心实现流程

```
文档上传
    │
    ▼
┌─────────────────┐
│ 1. 文件验证      │  ← 类型、大小检查
└─────────────────┘
    │
    ▼
┌─────────────────┐
│ 2. 保存文件      │  ← 存储到 uploads/ 目录
└─────────────────┘
    │
    ▼
┌─────────────────┐
│ 3. 解析文档      │  ← parse_document()
│   (多格式支持)   │     PDF/Word/MD/TXT/HTML
└─────────────────┘
    │
    ▼
┌─────────────────┐
│ 4. 文本分块      │  ← split_text()
│   (500字/块)    │     重叠50字保证语义完整
└─────────────────┘
    │
    ▼
┌─────────────────┐
│ 5. 向量化存储    │  ← vector_store.add_documents()
│   (ChromaDB)    │     每个知识库独立集合
└─────────────────┘
    │
    ▼
更新文档状态：processing → completed
```

### 2.3 重难点与解决方案

#### 难点 1：文档处理阻塞主线程

**问题**：文档解析和分块是 CPU 密集操作，直接在异步函数中执行会阻塞事件循环。

**解决方案**：使用 `asyncio.to_thread()` 包装同步函数。
```python
chunk_count = await asyncio.to_thread(
    process_document,
    kb_id=kb_id, doc_id=doc.id,
    file_path=file_path
)
```

#### 难点 2：分块重叠设计

**问题**：简单按固定长度切割会切断完整句子或段落。

**解决方案**：使用 `RecursiveCharacterTextSplitter`，按优先级分割：
1. 先按双换行 `\n\n` 分割（段落）
2. 再按单换行 `\n` 分割（句子）
3. 再按句号分割
4. 最后按空格分割
5. 重叠 50 字符确保上下文连续

#### 难点 3：向量数据与数据库一致性

**问题**：删除文档时，需要同时删除数据库记录和 ChromaDB 向量数据。

**解决方案**：
- 向量数据通过 metadata 中的 `doc_id` 字段关联
- 删除时使用 `collection.delete(where={"doc_id": doc_id})`
- 即使向量 ID 是随机生成的，也能精确删除

---

## 模块三：流式聊天 SSE

### 3.1 核心技术栈

#### SSE（Server-Sent Events）

**是什么？**
SSE 是一种服务器向客户端推送数据的技术，基于 HTTP 协议，支持流式传输。

**为什么用？**
- **实时性**：用户可以立即看到 AI 生成的内容，无需等待完整响应
- **体验好**：打字机效果，用户体验更流畅
- **简单可靠**：基于 HTTP，无需 WebSocket 的复杂性

**如何使用？**
```python
# 后端：使用 generator 生成 SSE 数据
async def chat_stream():
    yield f"data: {json.dumps({'type': 'chunk', 'content': '你好'})}\n\n"
    yield f"data: {json.dumps({'type': 'end'})}\n\n"

# 返回 StreamingResponse
return StreamingResponse(chat_stream(), media_type="text/event-stream")
```

```javascript
// 前端：使用 ReadableStream 解析
const reader = response.body.getReader()
const decoder = new TextDecoder()
let buffer = ''

while (true) {
    const { done, value } = await reader.read()
    if (done) break
    buffer += decoder.decode(value, { stream: true })
    const lines = buffer.split('\n')
    buffer = lines.pop()  // 保留不完整的行
    for (const line of lines) {
        if (line.startsWith('data: ')) {
            const event = JSON.parse(line.slice(6))
            // 处理事件
        }
    }
}
```

### 3.2 核心实现流程

```
前端发起请求
    │
    ▼
┌─────────────────┐
│ 后端返回         │
│ StreamingResponse│
└─────────────────┘
    │
    ▼
┌─────────────────┐
│ SSE 事件流       │
│                 │
│ data: {"type":"start","conversation_id":"xxx"}  ← 开始
│ data: {"type":"chunk","content":"你"}           ← 内容片段
│ data: {"type":"chunk","content":"好"}
│ data: {"type":"sources","documents":[...]}      ← 来源引用
│ data: {"type":"end","message_id":"xxx"}         ← 结束
└─────────────────┘
    │
    ▼
前端实时渲染内容
```

### 3.3 重难点与解决方案

#### 难点 1：分片解析

**问题**：SSE 数据可能跨多个 chunk 到达，需要正确拼接。

**解决方案**：使用 buffer 机制，保留最后一个不完整的行。
```javascript
buffer += decoder.decode(value, { stream: true })
const lines = buffer.split('\n')
buffer = lines.pop() || ''  // 保留可能不完整的行
for (const line of lines) {
    if (line.startsWith('data: ')) {
        const event = JSON.parse(line.slice(6))
    }
}
```

#### 难点 2：数据库 Session 作用域

**问题**：StreamingResponse 在 endpoint 返回后才消费生成器，此时 FastAPI 注入的 db session 已关闭。

**解决方案**：在生成器内部创建独立的 database session。
```python
async def chat_stream(data, db, user_id):
    # 使用独立 session，不依赖注入的 db
    async with async_session() as session:
        # 所有 DB 操作在这里
        ...
    # session 自动关闭
```

#### 难点 3：客户端断开处理

**问题**：用户关闭页面时，后端还在生成内容，可能导致资源浪费。

**解决方案**：
- 生成器检测到客户端断开会自动停止
- 使用 try/except 捕获异常，确保 session 正确关闭

---

## 模块四：JWT 认证体系

### 4.1 核心技术栈

#### Pydantic（数据验证）

**是什么？**
Pydantic 是 Python 的数据验证库，使用 Python 类型注解自动验证和序列化数据。FastAPI 内置支持 Pydantic。

**为什么用？**
- **自动验证**：请求参数自动验证，无需手动编写验证逻辑
- **类型安全**：利用 Python 类型注解，IDE 自动补全
- **序列化**：自动将数据转换为 JSON 格式

**如何使用？**
```python
from pydantic import BaseModel, Field

class UserCreate(BaseModel):
    username: str = Field(..., min_length=3, max_length=50)
    email: str = Field(..., regex=r'^[\w\.-]+@[\w\.-]+\.\w+$')
    password: str = Field(..., min_length=6)

# 自动验证
user = UserCreate(username="test", email="test@example.com", password="123456")
```

#### SQLAlchemy（ORM 框架）

**是什么？**
SQLAlchemy 是 Python 的 ORM（对象关系映射）框架，将数据库表映射为 Python 类，用对象操作代替 SQL 语句。

**为什么用？**
- **开发效率**：用 Python 代码操作数据库，无需手写 SQL
- **安全性**：自动防止 SQL 注入
- **跨数据库**：同一代码支持 MySQL、PostgreSQL、SQLite 等

**如何使用？**
```python
from sqlalchemy import Column, String, select
from sqlalchemy.ext.asyncio import AsyncSession

# 定义模型
class User(Base):
    __tablename__ = "users"
    id = Column(String(36), primary_key=True)
    username = Column(String(50), unique=True)

# 查询
result = await db.execute(select(User).where(User.username == "admin"))
user = result.scalar_one_or_none()
```

#### JWT（JSON Web Token）

**是什么？**
JWT 是一种开放标准（RFC 7519），用于在各方之间安全地传输信息。由三部分组成：
- **Header**：算法和类型
- **Payload**：数据（用户ID、角色、过期时间等）
- **Signature**：签名（防篡改）

**为什么用？**
- **无状态**：服务器不需要存储会话，适合分布式系统
- **跨域**：Token 可在不同域名间传递
- **自包含**：Token 本身包含用户信息，减少数据库查询

**如何使用？**
```python
# 签发 Token
token = jwt.encode(
    {"sub": user_id, "role": "user", "exp": expire, "jti": jti},
    secret_key,
    algorithm="HS256"
)

# 验证 Token
payload = jwt.decode(token, secret_key, algorithms=["HS256"])
```

#### PBKDF2 密码哈希

**是什么？**
PBKDF2（Password-Based Key Derivation Function 2）是一种密钥派生函数，通过多次迭代哈希来增强密码安全性。

**为什么用？**
- **抗暴力破解**：100,000 次迭代大大增加破解成本
- **防彩虹表**：每个密码使用随机盐值
- **常量时间比较**：使用 `hmac.compare_digest()` 防止时序攻击

**如何使用？**
```python
# 哈希密码
salt = secrets.token_hex(16)
hash_obj = hashlib.pbkdf2_hmac('sha256', password.encode(), salt.encode(), 100000)
return f"{salt}${hash_obj.hex()}"

# 验证密码
salt, hash_hex = hashed_password.split('$')
hash_obj = hashlib.pbkdf2_hmac('sha256', plain_password.encode(), salt.encode(), 100000)
return hmac.compare_digest(hash_obj.hex(), hash_hex)
```

### 4.2 核心实现流程

```
用户登录
    │
    ▼
┌─────────────────┐
│ 1. 频率限制检查  │  ← 基于 IP，5分钟10次上限
└─────────────────┘
    │
    ▼
┌─────────────────┐
│ 2. 查询用户      │  ← 支持用户名或邮箱
└─────────────────┘
    │
    ▼
┌─────────────────┐
│ 3. 验证密码      │  ← PBKDF2 + hmac.compare_digest
└─────────────────┘
    │
    ▼
┌─────────────────┐
│ 4. 生成 Token    │  ← Access Token (60分钟)
│                 │     Refresh Token (7天)
└─────────────────┘
    │
    ▼
返回 Token + 用户信息
```

### 4.3 重难点与解决方案

#### 难点 1：Refresh Token 安全

**问题**：Refresh Token 被盗用后无法撤销。

**解决方案**：实现 Token 轮换机制
```python
# 刷新时撤销旧 Token
def refresh_token(data):
    payload = decode_token(data.refresh_token)
    token_jti = payload.get("jti")
    
    # 检查是否已撤销
    if is_token_revoked(token_jti):
        raise ValidationError("Token 已被撤销")
    
    # 撤销旧 Token
    revoke_token(token_jti)
    
    # 签发新 Token
    new_access = create_access_token({"sub": user_id})
    new_refresh = create_refresh_token({"sub": user_id})
    return new_access, new_refresh
```

#### 难点 2：密码时序攻击

**问题**：使用 `==` 比较密码哈希可能被计时攻击破解。

**解决方案**：使用 `hmac.compare_digest()` 进行常量时间比较
```python
# ❌ 不安全：比较时间可能泄露信息
if hash1 == hash2: ...

# ✅ 安全：常量时间比较
if hmac.compare_digest(hash1, hash2): ...
```

---

## 模块五：知识库管理

### 5.1 核心功能

- **CRUD 操作**：创建、查询、更新、删除知识库
- **可见性控制**：公开/私有，官方知识库
- **知识库复制**：复制公开知识库的元数据和文档记录
- **分页查询**：支持 page/page_size 参数
- **权限控制**：私有知识库仅所有者可访问

### 5.2 核心实现流程

```
创建知识库
    │
    ▼
┌─────────────────┐
│ 1. 参数验证      │  ← Pydantic Schema
└─────────────────┘
    │
    ▼
┌─────────────────┐
│ 2. 创建 DB 记录  │  ← SQLAlchemy
└─────────────────┘
    │
    ▼
┌─────────────────┐
│ 3. 返回响应      │  ← 包含 ID、名称等
└─────────────────┘
```

### 5.3 重难点

#### 知识库复制设计

**问题**：复制知识库时，是否需要复制文档和向量数据？

**解决方案**：
- 复制元数据（名称、描述、分块配置）
- 复制文档记录（状态重置为 pending）
- **不复制向量数据**（需要用户重新上传处理）
- 复制文件（如果源文件存在，使用 `shutil.copy2()`）

---

## 项目答辩话术

### 开场介绍

> 我的项目是一个基于 RAG 技术的智能知识问答系统。用户可以上传文档到知识库，系统会自动解析、分块、向量化并存储，然后通过 AI 模型对用户的问题进行检索增强生成回答。核心技术亮点是 RAG 检索增强生成、向量检索、流式响应和多轮对话。

### 技术选型说明

> 后端使用 Python + FastAPI，选择 FastAPI 是因为它原生支持异步，性能优秀，且自带 API 文档。数据库使用 MySQL + ChromaDB，MySQL 存储结构化数据，ChromaDB 存储向量数据。LLM 使用 Ollama 本地部署，保证数据隐私。前端使用 Vue 3 + Element Plus，Pinia 管理状态。

### 核心功能演示

> 系统的核心流程是：用户上传文档 → 系统解析分块 → 向量化存入 ChromaDB → 用户提问时检索相关文档 → 构建 Prompt → LLM 生成回答。整个过程支持流式输出，用户体验像 ChatGPT 一样流畅。

### 难点突破

> 项目中遇到的最大挑战是向量检索与异步框架的兼容性问题。ChromaDB 的查询是同步的，直接调用会阻塞 FastAPI 的事件循环。我使用 `asyncio.to_thread()` 将同步操作放到线程池中执行，既保证了检索效率，又不影响其他请求的处理。

---

## 简历编写指南

### 项目描述（简洁版）

> **知识问答系统** | Python + FastAPI + Vue 3 + ChromaDB + Ollama
>
> 基于 RAG 技术的智能知识问答平台，支持多格式文档上传、向量化存储、流式响应和多轮对话。
> - 实现 RAG 检索增强生成流程，结合 ChromaDB 向量检索和 Ollama 本地 LLM
> - 设计流式聊天架构，使用 SSE 实现实时响应，支持打字机效果
> - 实现 JWT 双 Token 认证体系，支持 Token 轮换和频率限制
> - 处理异步框架与同步向量库的兼容性问题，使用线程池避免事件循环阻塞

### 技术亮点（详细版）

> **RAG 智能问答**
> - 设计完整的 RAG 流程：文档解析 → 文本分块 → 向量化 → 检索 → 生成
> - 使用 ChromaDB 存储文档向量，支持余弦相似度检索
> - 实现相似度阈值过滤，确保检索结果质量
>
> **流式响应架构**
> - 基于 SSE 实现流式输出，支持实时内容渲染
> - 使用 buffer 机制处理分片数据，确保数据完整性
> - 设计独立 session 管理，解决 StreamingResponse 的 session 作用域问题
>
> **安全设计**
> - 实现 JWT 双 Token 认证，Access Token 60分钟 + Refresh Token 7天
> - 使用 PBKDF2 + 盐值存储密码，hmac.compare_digest 防止时序攻击
> - 实现 Token 轮换机制，Refresh Token 使用后立即失效
> - 基于 IP 的频率限制，防止暴力破解

---

## 面试话术与高频问题

### 话术模板

> 我的项目是一个基于 RAG 技术的智能知识问答系统。RAG 的核心思想是「检索 + 生成」——先从知识库中检索相关文档，再让 LLM 基于这些文档生成回答。这样做的好处是减少 AI 幻觉，确保回答有据可依。
>
> 技术栈方面，后端用 FastAPI + SQLAlchemy，向量存储用 ChromaDB，LLM 用 Ollama 本地部署。前端是 Vue 3 + Element Plus。
>
> 项目中我遇到的最大挑战是 [具体问题]，我通过 [解决方案] 解决了这个问题。

### 高频面试问题

#### Q1: 为什么选择 RAG 而不是微调模型？

**答**：主要考虑三个因素：
1. **成本**：微调需要大量计算资源和标注数据，RAG 只需存储文档向量
2. **灵活性**：RAG 可以随时更新知识库，微调需要重新训练
3. **可解释性**：RAG 的每个回答都有来源引用，用户可以验证

#### Q2: 向量检索的原理是什么？

**答**：向量检索基于 Embedding 技术。首先用 Embedding 模型将文本转换为高维向量（如 768 维），然后通过余弦相似度计算向量间的距离。ChromaDB 使用 HNSW 算法实现近似最近邻搜索，可以在百万级数据中毫秒级返回最相似的结果。

#### Q3: 如何保证回答质量？

**答**：我从三个方面保证：
1. **检索质量**：设置相似度阈值（0.3），过滤不相关的结果
2. **Prompt 设计**：明确要求 LLM 只基于参考内容回答，不确定时说明
3. **来源引用**：每个回答标注参考来源，用户可以验证

#### Q4: 流式响应是怎么实现的？

**答**：后端使用 FastAPI 的 StreamingResponse + async generator，每个 LLM 输出的 chunk 作为 SSE 事件发送。前端使用 fetch + ReadableStream 接收数据，通过 buffer 机制处理分片问题。这样用户可以实时看到 AI 生成的内容，体验像 ChatGPT 一样。

#### Q5: 为什么选择 ChromaDB 而不是 Milvus？

**答**：主要考虑部署复杂度。ChromaDB 是轻量级的，几行代码即可集成，支持本地持久化，适合中小型项目。Milvus 是分布式向量数据库，适合大规模生产环境，但部署和运维成本更高。对于我的项目规模，ChromaDB 完全够用。

#### Q6: 多轮对话是怎么实现的？

**答**：每次用户提问时，我会从数据库中加载最近 5 轮对话历史，格式化后注入到 Prompt 中。这样 LLM 可以理解上下文，支持追问和澄清。历史消息会截断到 500 字符，避免超过 LLM 的上下文窗口限制。

#### Q7: 如何处理 LLM 超时？

**答**：使用 `asyncio.wait_for()` 设置 120 秒超时。如果超时，返回友好提示「AI 模型响应超时，请稍后重试」。同时在前端实现重试机制，用户可以重新发送问题。

#### Q8: 密码存储安全吗？

**答**：使用 PBKDF2 算法 + 随机盐值存储密码，迭代 100,000 次。验证时使用 `hmac.compare_digest()` 进行常量时间比较，防止时序攻击。即使数据库泄露，攻击者也很难暴力破解密码。

#### Q9: 项目有哪些可以优化的地方？

**答**：
1. **缓存**：可以添加 Redis 缓存热点知识库和设置项
2. **分页**：已经实现了分页，但前端可以添加无限滚动
3. **测试**：需要补充单元测试和集成测试
4. **部署**：可以容器化部署，使用 Docker Compose 编排

#### Q10: 如果用户量增大，系统如何扩展？

**答**：
1. **水平扩展**：FastAPI 支持多 worker 部署，可以增加实例
2. **数据库**：MySQL 可以读写分离，ChromaDB 可以切换到 Milvus
3. **缓存**：引入 Redis 缓存热点数据
4. **LLM**：Ollama 可以部署多实例，或切换到云端 API

---

## 附录 A：错误处理与异常体系

### 异常类设计

```python
# 自定义异常基类
class AppException(HTTPException):
    def __init__(self, status_code, code, message, detail=None):
        super().__init__(status_code=status_code, detail=message)
        self.code = code
        self.message = message
        self.detail = detail or {}

# 业务异常
class NotFoundError(AppException):      # 404
class ValidationError(AppException):    # 422
class PermissionDeniedError(AppException):  # 403
class UnauthorizedError(AppException):  # 401
```

### 全局异常处理

```python
# FastAPI 异常处理器
@app.exception_handler(AppException)
async def app_exception_handler(request, exc):
    return JSONResponse(
        status_code=exc.status_code,
        content={"error": {"code": exc.code, "message": exc.message}}
    )
```

### 前端错误处理

```javascript
// axios 响应拦截器
api.interceptors.response.use(
  (response) => response,
  (error) => {
    const status = error.response?.status
    if (status === 401) {
      localStorage.removeItem('token')
      window.location.href = '/login'
    }
    ElMessage.error(error.response?.data?.error?.message || '请求失败')
    return Promise.reject(error)
  }
)
```

---

## 附录 B：项目文件结构

```
knowledge-qa/
├── backend/
│   ├── app/
│   │   ├── api/              # API 路由
│   │   │   ├── auth.py       # 认证
│   │   │   ├── chat.py       # 聊天
│   │   │   ├── knowledge_base.py
│   │   │   └── ...
│   │   ├── core/             # 核心模块
│   │   │   ├── security.py   # JWT + 密码
│   │   │   ├── database.py   # 数据库
│   │   │   ├── chunker.py    # 文本分块
│   │   │   └── document_parser.py
│   │   ├── services/         # 业务逻辑
│   │   │   ├── chat.py       # RAG 问答
│   │   │   ├── llm.py        # LLM 服务
│   │   │   ├── vector_store.py
│   │   │   └── ...
│   │   ├── models/           # 数据模型
│   │   ├── schemas/          # Pydantic 模式
│   │   └── main.py           # 应用入口
│   └── requirements.txt
├── user-web/                 # 用户端前端
│   └── src/
│       ├── views/            # 页面组件
│       ├── api/              # API 调用
│       ├── stores/           # Pinia 状态
│       └── router/           # 路由配置
└── admin-web/                # 管理端前端
```

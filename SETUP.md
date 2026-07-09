# 环境搭建操作文档

本文档包含所有需要手动操作的配置步骤。

---

## 1. 前置要求

| 软件 | 版本要求 | 安装方式 |
|------|---------|---------|
| Python | >= 3.10 | https://www.python.org/downloads/ |
| Node.js | >= 18 | https://nodejs.org/ |
| MySQL | >= 5.7 | https://dev.mysql.com/downloads/ |
| Ollama | 最新版本 | https://ollama.com/download |

---

## 2. MySQL 数据库配置

### 2.1 启动 MySQL 服务

**Windows:**
```powershell
# 方法一：通过服务管理器
net start mysql80

# 方法二：命令行（需管理员权限）
sc start mysql80
```

**macOS:**
```bash
brew services start mysql
```

**Linux:**
```bash
sudo systemctl start mysql
```

### 2.2 登录并创建数据库

```sql
-- 登录 MySQL
mysql -u root -p

-- 创建数据库
CREATE DATABASE knowledge_qa
  CHARACTER SET utf8mb4
  COLLATE utf8mb4_unicode_ci;

-- 验证
SHOW DATABASES;
```

### 2.3 修改数据库密码（可选）

```sql
-- 将 root 密码改为 123456（与 .env 文件一致）
ALTER USER 'root'@'localhost' IDENTIFIED BY '123456';
FLUSH PRIVILEGES;
```

---

## 3. Ollama 安装与配置

### 3.1 安装 Ollama

访问 https://ollama.com/download 下载对应系统版本。

### 3.2 拉取模型

```bash
# 中文模型（推荐）
ollama pull qwen2:7b

# 或者其他模型
ollama pull llama3
ollama pull mistral
```

### 3.3 验证 Ollama 服务

```bash
# 检查服务是否运行
curl http://localhost:11434/api/tags

# 测试对话
ollama run qwen2:7b "你好"
```

---

## 4. 后端环境配置

### 4.1 创建虚拟环境

```bash
cd knowledge-qa/backend

# 创建虚拟环境
python -m venv venv

# 激活虚拟环境
# Windows:
venv\Scripts\activate
# macOS/Linux:
source venv/bin/activate
```

### 4.2 安装依赖

```bash
pip install -r requirements.txt
```

### 4.3 配置环境变量

```bash
# 复制示例配置
cp .env.example .env

# 编辑 .env 文件，修改数据库密码
```

**.env 关键配置项：**

```env
# 数据库连接（修改密码为你实际的 MySQL 密码）
DATABASE_URL=mysql+aiomysql://root:123456@localhost:3306/knowledge_qa

# Ollama 配置（确保 Ollama 服务已启动）
OLLAMA_BASE_URL=http://localhost:11434
OLLAMA_MODEL=qwen2:7b
```

### 4.4 启动后端服务

```bash
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

验证：浏览器访问 http://localhost:8000/docs 查看 API 文档。

---

## 5. 前端环境配置

### 5.1 安装依赖

```bash
cd knowledge-qa/frontend
npm install
```

### 5.2 启动开发服务器

```bash
npm run dev
```

验证：浏览器访问 http://localhost:5173。  

---

## 6. 嵌入模型首次加载

首次使用时，`sentence-transformers` 会自动下载 `BAAI/bge-small-zh-v1.5` 模型（约 100MB）。

如需手动下载或使用国内镜像：

```bash
# 设置 HuggingFace 镜像（可选）
export HF_ENDPOINT=https://hf-mirror.com

# 预下载模型
python -c "from sentence_transformers import SentenceTransformer; SentenceTransformer('BAAI/bge-small-zh-v1.5')"
```

---

## 7. 常见问题

### Q: 数据库连接失败
```
检查：
1. MySQL 服务是否启动
2. .env 中 DATABASE_URL 的密码是否正确
3. 数据库 knowledge_qa 是否已创建
```

### Q: Ollama 连接失败
```
检查：
1. Ollama 服务是否运行（http://localhost:11434）
2. 模型是否已拉取（ollama list）
3. 防火墙是否放行 11434 端口
```

### Q: 前端页面空白
```
检查：
1. 后端是否启动（http://localhost:8000）
2. 浏览器控制台是否有错误
3. vite.config.js 中的代理配置
```

---

## 8. 启动顺序

1. 启动 MySQL 服务
2. 启动 Ollama 服务
3. 启动后端：`cd backend && uvicorn app.main:app --reload`
4. 启动前端：`cd frontend && npm run dev`
5. 访问 http://localhost:5173

---

## 9. 当前环境状态

| 项目 | 状态 | 说明 |
|------|------|------|
| Python 3.12.6 | ✅ 已安装 | |
| Node.js 24.15.0 | ✅ 已安装 | |
| MySQL 5.7 | ✅ 已安装，已创建 knowledge_qa 数据库 | 密码：root |
| Ollama 0.30.0 | ✅ 已安装，qwen2:7b 已拉取 | |
| 后端依赖 | ✅ 已安装 | |
| 前端依赖 | ✅ 已安装 | |
| 后端服务 | ✅ 运行中 | http://localhost:8000 |
| 前端服务 | ✅ 运行中 | http://localhost:5173 |
| RAG 功能 | ✅ 已实现 | 文档解析、分块、嵌入、问答链 |

### 快速启动命令

```bash
# 后端
cd knowledge-qa/backend
python -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

# 前端
cd knowledge-qa/frontend
npm run dev
```

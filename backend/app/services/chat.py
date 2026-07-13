"""聊天服务 - RAG 问答链"""
import re
import asyncio
from app.config import settings
from app.services.vector_store import get_vector_store
from app.services.llm import get_llm_service

# 敏感词列表（可根据需要扩展）
SENSITIVE_WORDS = [
    # 违法违规
    "赌博", "毒品", "枪支", "爆炸", "恐怖", "贩卖", "走私", "洗钱",
    # 歧视侮辱
    "歧视", "侮辱", "谩骂", "诽谤", "人身攻击",
    # 个人隐私
    "身份证号", "银行卡号", "密码", "手机号码", "家庭住址",
    # 危险行为
    "自杀", "自残", "纵火",
]

# RAG 提示模板 - 支持多轮对话
RAG_PROMPT_TEMPLATE = """你是一个专业的知识问答助手。请严格根据以下参考内容回答用户的问题。

## 重要规则：
1. **必须基于参考内容回答**：只能使用参考内容中的信息来回答，不要添加参考内容中没有的信息
2. **必须标注来源**：在回答中引用具体信息时，请使用 [来源X] 的格式标注来自哪条参考内容，并注明文件名
3. **不确定时明确说明**：如果参考内容中没有足够的信息来回答问题，请明确告诉用户"根据现有知识，无法找到相关信息"
4. **不要编造答案**：宁可说不知道，也不要猜测或编造信息
5. **结合对话历史**：参考之前的对话内容，理解用户的意图和上下文

## 参考内容：
{context}

## 对话历史：
{history}

## 用户问题：
{question}

## 回答要求：
- 使用中文回答
- 回答要准确、简洁
- 在引用信息时标注 [来源X] 和文件名
- 结合对话历史理解上下文
- 如果没有相关信息，直接说明无法回答"""

# 非 RAG 模式提示（无相关文档时）
NO_CONTEXT_PROMPT = """你是一个知识问答助手。用户问了一个问题，但在知识库中没有找到相关信息。

## 对话历史：
{history}

## 用户问题：
{question}

请用中文简短回复，告诉用户当前知识库中没有相关信息，建议用户上传相关文档。"""


def check_sensitive_content(text: str) -> tuple[bool, str]:
    """检查敏感内容"""
    if not text:
        return True, text

    for word in SENSITIVE_WORDS:
        pattern = r'[\s\-_]*'.join(list(word))
        if re.search(pattern, text):
            return False, f"内容包含敏感词：{word}"
    return True, text


def filter_response(text: str) -> str:
    """过滤 AI 回答中的不当内容"""
    if not text:
        return text

    for word in SENSITIVE_WORDS:
        pattern = r'[\s\-_]*'.join(list(word))
        text = re.sub(pattern, "***", text)
    return text


def format_history(history: list[dict], max_turns: int = 5) -> str:
    """格式化对话历史"""
    if not history:
        return "暂无对话历史"

    recent_history = history[-(max_turns * 2):]

    formatted = []
    for msg in recent_history:
        role = "用户" if msg["role"] == "user" else "助手"
        content = msg["content"][:500]
        formatted.append(f"{role}：{content}")

    return "\n".join(formatted)


async def rag_chat(file_ids: list[str], question: str, history: list[dict] = None):
    """
    RAG 问答（支持多轮对话，自动匹配文件）

    Args:
        file_ids: 用户的所有文件 ID 列表
        question: 用户问题
        history: 对话历史消息列表

    Yields:
        (chunk, sources) 元组，chunk 是文本片段，sources 是来源引用
    """
    # 检查用户输入
    is_safe, msg = check_sensitive_content(question)
    if not is_safe:
        yield "您的问题包含不当内容，无法回答。", []
        return

    vector_store = get_vector_store()
    llm = get_llm_service()

    # 格式化对话历史
    history_text = format_history(history or [])

    # 相似度阈值
    try:
        similarity_threshold = float(getattr(settings, "SIMILARITY_THRESHOLD", "0.3"))
    except (ValueError, AttributeError):
        similarity_threshold = 0.3

    # 跨文件检索：从用户的所有文件中检索最相关的内容
    all_results = []
    for file_id in file_ids:
        try:
            results = await asyncio.to_thread(vector_store.query, file_id, question, 3)
            for doc in results:
                if doc["score"] >= similarity_threshold:
                    all_results.append(doc)
        except Exception:
            continue

    # 按相似度排序，取 Top-5
    all_results.sort(key=lambda x: x["score"], reverse=True)
    top_results = all_results[:5]

    sources = []
    context_parts = []
    for i, doc in enumerate(top_results):
        context_parts.append(f"[来源{i+1}] {doc['content']}")
        sources.append({
            "doc_id": doc["metadata"].get("doc_id", ""),
            "doc_filename": doc["metadata"].get("filename", "未知文件"),
            "chunk_id": doc["id"],
            "content": doc["content"][:200],
            "score": round(doc["score"], 3),
        })

    if not context_parts:
        # 没有相关文档
        prompt = NO_CONTEXT_PROMPT.format(history=history_text, question=question)
        async for chunk in llm.stream_chat(prompt):
            yield filter_response(chunk), []
    else:
        # 有相关文档
        context = "\n\n".join(context_parts)
        prompt = RAG_PROMPT_TEMPLATE.format(
            context=context,
            history=history_text,
            question=question
        )

        async for chunk in llm.stream_chat(prompt):
            yield filter_response(chunk), sources


def process_document(kb_id: str, doc_id: str, file_path: str, filename: str = "", chunk_size: int = 500, chunk_overlap: int = 50):
    """
    处理文档：解析 -> 分块 -> 嵌入 -> 存储

    Args:
        kb_id: collection ID（现在使用 doc_id）
        doc_id: 文档 ID
        file_path: 文件路径
        filename: 文件名（用于元数据）
        chunk_size: 分块大小
        chunk_overlap: 分块重叠
    """
    from app.core.document_parser import parse_document
    from app.core.chunker import split_text
    import uuid

    # 1. 解析文档
    text = parse_document(file_path)
    if not text.strip():
        raise ValueError("文档内容为空")

    # 2. 分块
    chunks = split_text(text, chunk_size=chunk_size, chunk_overlap=chunk_overlap)
    if not chunks:
        raise ValueError("分块失败")

    # 3. 嵌入并存储
    vector_store = get_vector_store()

    ids = [str(uuid.uuid4()) for _ in chunks]
    for i, chunk in enumerate(chunks):
        chunk["metadata"]["doc_id"] = doc_id
        chunk["metadata"]["filename"] = filename

    vector_store.add_documents(kb_id, chunks, ids)

    return len(chunks)

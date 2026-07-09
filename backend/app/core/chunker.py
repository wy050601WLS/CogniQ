"""文本分块器"""
from langchain_text_splitters import RecursiveCharacterTextSplitter


def split_text(
    text: str,
    chunk_size: int = 500,
    chunk_overlap: int = 50,
) -> list[dict]:
    """
    将文本分割成 chunks

    Args:
        text: 原始文本
        chunk_size: 每个 chunk 的最大字符数
        chunk_overlap: chunk 之间的重叠字符数

    Returns:
        分块列表，每个元素包含 content 和 metadata
    """
    if not text or not text.strip():
        return []

    splitter = RecursiveCharacterTextSplitter(
        chunk_size=chunk_size,
        chunk_overlap=chunk_overlap,
        length_function=len,
        separators=["\n\n", "\n", "。", "！", "？", ".", "!", "?", " ", ""],
    )

    chunks = splitter.split_text(text)
    result = []
    for i, chunk in enumerate(chunks):
        if chunk.strip():
            result.append({
                "content": chunk.strip(),
                "metadata": {
                    "chunk_index": i,
                    "chunk_size": len(chunk),
                }
            })
    return result

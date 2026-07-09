"""分块器测试"""
from app.core.chunker import split_text


class TestChunker:
    """文本分块器测试"""

    def test_split_simple_text(self):
        """测试简单文本分块"""
        text = "这是一段测试文本。" * 100
        chunks = split_text(text, chunk_size=100, chunk_overlap=20)
        assert len(chunks) > 0
        for chunk in chunks:
            assert "content" in chunk
            assert "metadata" in chunk
            assert len(chunk["content"]) <= 150  # 允许一定误差

    def test_split_empty_text(self):
        """测试空文本"""
        chunks = split_text("", chunk_size=100, chunk_overlap=20)
        assert chunks == []

    def test_split_short_text(self):
        """测试短文本"""
        text = "短文本"
        chunks = split_text(text, chunk_size=100, chunk_overlap=20)
        assert len(chunks) == 1
        assert chunks[0]["content"] == "短文本"

    def test_split_preserves_content(self):
        """测试内容完整性"""
        text = "第一段内容。\n\n第二段内容。\n\n第三段内容。"
        chunks = split_text(text, chunk_size=50, chunk_overlap=10)
        full_content = "".join(c["content"] for c in chunks)
        assert "第一段" in full_content
        assert "第二段" in full_content
        assert "第三段" in full_content

    def test_split_metadata(self):
        """测试元数据"""
        text = "测试文本" * 50
        chunks = split_text(text, chunk_size=100, chunk_overlap=20)
        for i, chunk in enumerate(chunks):
            assert chunk["metadata"]["chunk_index"] == i
            assert "chunk_size" in chunk["metadata"]

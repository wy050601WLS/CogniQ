"""嵌入模型服务"""
from functools import lru_cache
from sentence_transformers import SentenceTransformer
from app.config import settings


class EmbeddingService:
    """嵌入模型服务"""

    def __init__(self, model_name: str = None):
        self.model_name = model_name or settings.EMBEDDING_MODEL
        self._model = None

    @property
    def model(self):
        if self._model is None:
            self._model = SentenceTransformer(self.model_name)
        return self._model

    def embed_documents(self, texts: list[str]) -> list[list[float]]:
        """批量嵌入文档"""
        embeddings = self.model.encode(texts, show_progress_bar=False)
        return embeddings.tolist()

    def embed_query(self, text: str) -> list[float]:
        """嵌入查询"""
        embedding = self.model.encode([text], show_progress_bar=False)
        return embedding[0].tolist()


@lru_cache()
def get_embedding_service() -> EmbeddingService:
    """获取嵌入服务单例"""
    return EmbeddingService()

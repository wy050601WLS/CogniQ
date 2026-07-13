"""向量存储服务 - Chroma"""
import logging
import threading
import chromadb
from app.config import settings

logger = logging.getLogger(__name__)


class VectorStoreService:
    """Chroma 向量存储服务"""

    def __init__(self):
        self.client = chromadb.PersistentClient(path=settings.CHROMA_PERSIST_DIR)

    def get_or_create_collection(self, doc_id: str):
        """获取或创建集合（每个文件一个 collection）"""
        collection_name = f"file_{doc_id}"
        return self.client.get_or_create_collection(
            name=collection_name,
            metadata={"hnsw:space": "cosine"},
        )

    def add_documents(self, doc_id: str, documents: list[dict], ids: list[str]):
        """添加文档到向量存储"""
        collection = self.get_or_create_collection(doc_id)
        contents = [doc["content"] for doc in documents]
        metadatas = [doc.get("metadata", {}) for doc in documents]
        collection.add(
            documents=contents,
            metadatas=metadatas,
            ids=ids,
        )

    def query(self, doc_id: str, query_text: str, n_results: int = 5) -> list[dict]:
        """查询相关文档"""
        collection = self.get_or_create_collection(doc_id)
        results = collection.query(
            query_texts=[query_text],
            n_results=n_results,
        )
        docs = []
        if results and results["documents"]:
            for i, doc in enumerate(results["documents"][0]):
                metadata = results["metadatas"][0][i] if results["metadatas"] else {}
                distance = results["distances"][0][i] if results["distances"] else 0
                chunk_id = results["ids"][0][i] if results["ids"] else ""
                docs.append({
                    "content": doc,
                    "metadata": metadata,
                    "score": 1 - distance,  # cosine distance -> similarity
                    "id": chunk_id,
                })
        return docs

    def delete_collection(self, doc_id: str):
        """删除集合"""
        collection_name = f"file_{doc_id}"
        try:
            self.client.delete_collection(collection_name)
        except Exception:
            pass

    def delete_documents(self, doc_id: str):
        """删除文件的所有向量数据"""
        self.delete_collection(doc_id)

    def delete_by_metadata(self, doc_id: str, where: dict):
        """根据 metadata 条件删除向量数据"""
        collection = self.get_or_create_collection(doc_id)
        try:
            collection.delete(where=where)
        except Exception as e:
            logger.warning(f"根据条件删除向量数据失败 (doc={doc_id}, where={where}): {e}")


_vector_store = None
_vector_store_lock = threading.Lock()


def get_vector_store() -> VectorStoreService:
    """获取向量存储服务单例（线程安全）"""
    global _vector_store
    if _vector_store is None:
        with _vector_store_lock:
            if _vector_store is None:
                _vector_store = VectorStoreService()
    return _vector_store

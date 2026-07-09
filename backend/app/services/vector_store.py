"""向量存储服务 - Chroma"""
import logging
import chromadb
from app.config import settings

logger = logging.getLogger(__name__)


class VectorStoreService:
    """Chroma 向量存储服务"""

    def __init__(self):
        self.client = chromadb.PersistentClient(path=settings.CHROMA_PERSIST_DIR)

    def get_or_create_collection(self, kb_id: str):
        """获取或创建集合"""
        collection_name = f"{settings.CHROMA_COLLECTION_PREFIX}{kb_id}"
        return self.client.get_or_create_collection(
            name=collection_name,
            metadata={"hnsw:space": "cosine"},
        )

    def add_documents(self, kb_id: str, documents: list[dict], ids: list[str]):
        """添加文档到向量存储"""
        collection = self.get_or_create_collection(kb_id)
        contents = [doc["content"] for doc in documents]
        metadatas = [doc.get("metadata", {}) for doc in documents]
        collection.add(
            documents=contents,
            metadatas=metadatas,
            ids=ids,
        )

    def query(self, kb_id: str, query_text: str, n_results: int = 5) -> list[dict]:
        """查询相关文档"""
        collection = self.get_or_create_collection(kb_id)
        results = collection.query(
            query_texts=[query_text],
            n_results=n_results,
        )
        docs = []
        if results and results["documents"]:
            for i, doc in enumerate(results["documents"][0]):
                metadata = results["metadatas"][0][i] if results["metadatas"] else {}
                distance = results["distances"][0][i] if results["distances"] else 0
                doc_id = results["ids"][0][i] if results["ids"] else ""
                docs.append({
                    "content": doc,
                    "metadata": metadata,
                    "score": 1 - distance,  # cosine distance -> similarity
                    "id": doc_id,
                })
        return docs

    def delete_collection(self, kb_id: str):
        """删除集合"""
        collection_name = f"{settings.CHROMA_COLLECTION_PREFIX}{kb_id}"
        try:
            self.client.delete_collection(collection_name)
        except Exception:
            pass

    def delete_documents(self, kb_id: str, doc_ids: list[str]):
        """根据文档 ID 删除向量数据（通过 metadata 中的 doc_id 字段匹配）"""
        collection = self.get_or_create_collection(kb_id)
        try:
            # ChromaDB 的 delete 支持 where 条件删除
            # 由于向量数据的 ID 是随机生成的，需要通过 metadata 中的 doc_id 来删除
            for doc_id in doc_ids:
                collection.delete(where={"doc_id": doc_id})
        except Exception as e:
            logger.warning(f"删除向量数据失败 (kb={kb_id}, docs={doc_ids}): {e}")

    def delete_by_metadata(self, kb_id: str, where: dict):
        """根据 metadata 条件删除向量数据"""
        collection = self.get_or_create_collection(kb_id)
        try:
            collection.delete(where=where)
        except Exception as e:
            logger.warning(f"根据条件删除向量数据失败 (kb={kb_id}, where={where}): {e}")


_vector_store = None


def get_vector_store() -> VectorStoreService:
    """获取向量存储服务单例"""
    global _vector_store
    if _vector_store is None:
        _vector_store = VectorStoreService()
    return _vector_store

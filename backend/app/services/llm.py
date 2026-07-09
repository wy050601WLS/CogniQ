"""LLM 服务 - Ollama"""
import asyncio
from typing import AsyncGenerator
import ollama
from app.config import settings

# LLM 调用超时时间（秒）
LLM_TIMEOUT_SECONDS = 120


class LLMService:
    """LLM 服务封装"""

    def __init__(self):
        self.client = ollama.AsyncClient(host=settings.OLLAMA_BASE_URL)

    async def stream_chat(self, prompt: str, model: str = None) -> AsyncGenerator[str, None]:
        """流式聊天（异步，带超时控制）"""
        model = model or settings.OLLAMA_MODEL
        try:
            stream = await asyncio.wait_for(
                self.client.chat(
                    model=model,
                    messages=[{"role": "user", "content": prompt}],
                    stream=True,
                ),
                timeout=LLM_TIMEOUT_SECONDS,
            )
            async for chunk in stream:
                if chunk["message"]["content"]:
                    yield chunk["message"]["content"]
        except asyncio.TimeoutError:
            yield "抱歉，AI 模型响应超时，请稍后重试"
        except Exception as e:
            yield f"抱歉，AI 模型调用失败：{type(e).__name__}"

    async def chat(self, prompt: str, model: str = None) -> str:
        """非流式聊天（异步，带超时控制）"""
        model = model or settings.OLLAMA_MODEL
        try:
            response = await asyncio.wait_for(
                self.client.chat(
                    model=model,
                    messages=[{"role": "user", "content": prompt}],
                ),
                timeout=LLM_TIMEOUT_SECONDS,
            )
            return response["message"]["content"]
        except asyncio.TimeoutError:
            return "抱歉，AI 模型响应超时，请稍后重试"
        except Exception as e:
            return f"抱歉，AI 模型调用失败：{type(e).__name__}"

    async def list_models(self) -> list[str]:
        """列出可用模型（异步）"""
        models = await self.client.list()
        return [m["name"] for m in models]


_llm_service = None


def get_llm_service() -> LLMService:
    """获取 LLM 服务单例"""
    global _llm_service
    if _llm_service is None:
        _llm_service = LLMService()
    return _llm_service

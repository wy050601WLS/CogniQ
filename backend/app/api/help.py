"""帮助 API"""
from fastapi import APIRouter, Query
from app.data.help_content import HELP_CATEGORIES
from app.exceptions import NotFoundError

router = APIRouter()


@router.get("/help", summary="获取帮助内容列表")
async def get_help_categories():
    """获取所有帮助分类（含条目数量）"""
    return [
        {"id": cat["id"], "title": cat["title"], "icon": cat["icon"], "count": len(cat.get("items", []))}
        for cat in HELP_CATEGORIES
    ]


@router.get("/help/search", summary="搜索帮助内容")
async def search_help(q: str = Query(..., min_length=1)):
    """搜索帮助内容"""
    results = []
    query = q.lower()

    for cat in HELP_CATEGORIES:
        for item in cat["items"]:
            # 搜索标题、内容和标签（标签也转小写比较）
            if (query in item["title"].lower() or
                query in item.get("content", "").lower() or
                any(query in tag.lower() for tag in item.get("tags", []))):
                # 生成内容摘要（截取匹配位置前后的内容）
                content = item.get("content", "")
                snippet = ""
                content_lower = content.lower()
                pos = content_lower.find(query)
                if pos >= 0:
                    start = max(0, pos - 40)
                    end = min(len(content), pos + 60)
                    snippet = content[start:end].strip()
                    if start > 0:
                        snippet = "..." + snippet
                    if end < len(content):
                        snippet = snippet + "..."
                else:
                    snippet = content[:100].strip() + "..." if content else ""

                results.append({
                    "category": cat["title"],
                    "id": item["id"],
                    "title": item["title"],
                    "tags": item.get("tags", []),
                    "snippet": snippet,
                })

    return {"results": results, "total": len(results)}


@router.get("/help/item/{item_id}", summary="获取单个帮助内容")
async def get_help_item(item_id: str):
    """获取指定帮助项的详细内容"""
    for cat in HELP_CATEGORIES:
        for item in cat["items"]:
            if item["id"] == item_id:
                return {
                    "category": cat["title"],
                    **item
                }
    raise NotFoundError("帮助项", item_id)


@router.get("/help/{category_id}", summary="获取分类下的帮助内容")
async def get_help_items(category_id: str):
    """获取指定分类下的所有帮助项"""
    for cat in HELP_CATEGORIES:
        if cat["id"] == category_id:
            return {
                "id": cat["id"],
                "title": cat["title"],
                "icon": cat["icon"],
                "items": cat["items"]
            }
    raise NotFoundError("帮助分类", category_id)

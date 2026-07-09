"""帮助和设置 API 测试"""
import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_help_categories(client: AsyncClient):
    """测试获取帮助分类"""
    resp = await client.get("/api/help")
    assert resp.status_code == 200
    data = resp.json()
    assert isinstance(data, list)
    assert len(data) > 0
    assert "id" in data[0]
    assert "title" in data[0]


@pytest.mark.asyncio
async def test_help_search(client: AsyncClient):
    """测试帮助搜索"""
    resp = await client.get("/api/help/search?q=知识库")
    assert resp.status_code == 200
    data = resp.json()
    assert "results" in data
    assert "total" in data


@pytest.mark.asyncio
async def test_help_category_detail(client: AsyncClient):
    """测试获取分类详情"""
    resp = await client.get("/api/help/knowledge-base")
    assert resp.status_code == 200
    data = resp.json()
    assert data["id"] == "knowledge-base"
    assert "items" in data


@pytest.mark.asyncio
async def test_help_category_not_found(client: AsyncClient):
    """测试不存在的分类"""
    resp = await client.get("/api/help/nonexistent-category")
    assert resp.status_code == 404


@pytest.mark.asyncio
async def test_help_item_detail(client: AsyncClient):
    """测试获取帮助项详情"""
    resp = await client.get("/api/help/item/upload-doc")
    assert resp.status_code == 200
    data = resp.json()
    assert data["id"] == "upload-doc"
    assert "content" in data


@pytest.mark.asyncio
async def test_help_item_not_found(client: AsyncClient):
    """测试不存在的帮助项"""
    resp = await client.get("/api/help/item/nonexistent-item")
    assert resp.status_code == 404


@pytest.mark.asyncio
async def test_get_settings(client: AsyncClient):
    """测试获取系统设置"""
    resp = await client.get("/api/settings")
    assert resp.status_code == 200
    data = resp.json()
    assert "llm" in data
    assert "embedding" in data
    assert "chunking" in data


@pytest.mark.asyncio
async def test_update_settings_requires_admin(client: AsyncClient):
    """测试更新设置需要管理员权限"""
    # 普通用户
    reg_resp = await client.post("/api/auth/register", json={
        "username": "settings_test_user",
        "email": "settings_test@example.com",
        "password": "test123456",
    })
    user_token = reg_resp.json()["access_token"]

    resp = await client.put(
        "/api/settings",
        json={"chunking": {"chunk_size": 600}},
        headers={"Authorization": f"Bearer {user_token}"},
    )
    assert resp.status_code == 403


@pytest.mark.asyncio
async def test_update_settings_admin(client: AsyncClient):
    """测试管理员更新设置"""
    login_resp = await client.post("/api/auth/login", json={
        "username": "admin",
        "password": "admin123",
    })
    admin_token = login_resp.json()["access_token"]

    resp = await client.put(
        "/api/settings",
        json={"chunking": {"chunk_size": 500, "chunk_overlap": 50}},
        headers={"Authorization": f"Bearer {admin_token}"},
    )
    assert resp.status_code == 200

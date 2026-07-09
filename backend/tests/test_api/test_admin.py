"""管理后台 API 测试"""
import pytest
from httpx import AsyncClient


@pytest.fixture
async def admin_headers(client: AsyncClient) -> dict:
    """获取管理员 token"""
    resp = await client.post("/api/auth/login", json={
        "username": "admin",
        "password": "admin123",
    })
    token = resp.json()["access_token"]
    return {"Authorization": f"Bearer {token}"}


@pytest.mark.asyncio
async def test_admin_stats_overview(client: AsyncClient, admin_headers):
    """测试管理后台统计"""
    resp = await client.get("/api/admin/stats/overview", headers=admin_headers)
    assert resp.status_code == 200
    data = resp.json()
    assert "user_count" in data
    assert "knowledge_base_count" in data
    assert "document_count" in data


@pytest.mark.asyncio
async def test_admin_list_users(client: AsyncClient, admin_headers):
    """测试获取用户列表"""
    resp = await client.get("/api/admin/users", headers=admin_headers)
    assert resp.status_code == 200
    data = resp.json()
    assert isinstance(data, list)
    assert len(data) > 0


@pytest.mark.asyncio
async def test_admin_list_knowledge_bases(client: AsyncClient, admin_headers):
    """测试获取所有知识库"""
    resp = await client.get("/api/admin/knowledge-bases", headers=admin_headers)
    assert resp.status_code == 200
    data = resp.json()
    assert "items" in data


@pytest.mark.asyncio
async def test_admin_requires_admin_role(client: AsyncClient):
    """测试管理接口需要管理员权限"""
    # 普通用户
    reg_resp = await client.post("/api/auth/register", json={
        "username": "admin_test_normal",
        "email": "admin_test_normal@example.com",
        "password": "test123456",
    })
    user_token = reg_resp.json()["access_token"]

    resp = await client.get(
        "/api/admin/users",
        headers={"Authorization": f"Bearer {user_token}"},
    )
    assert resp.status_code == 403


@pytest.mark.asyncio
async def test_admin_requires_auth(client: AsyncClient):
    """测试管理接口需要登录"""
    resp = await client.get("/api/admin/users")
    assert resp.status_code == 401

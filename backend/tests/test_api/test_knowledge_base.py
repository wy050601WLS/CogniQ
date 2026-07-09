"""知识库 API 测试"""
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
async def test_list_my_knowledge_bases(client: AsyncClient, admin_headers):
    """测试获取我的知识库列表"""
    resp = await client.get("/api/knowledge-bases/my", headers=admin_headers)
    assert resp.status_code == 200
    data = resp.json()
    assert "items" in data
    assert "total" in data


@pytest.mark.asyncio
async def test_list_marketplace(client: AsyncClient, admin_headers):
    """测试知识库广场"""
    resp = await client.get("/api/knowledge-bases/marketplace", headers=admin_headers)
    assert resp.status_code == 200
    data = resp.json()
    assert "items" in data


@pytest.mark.asyncio
async def test_create_knowledge_base(client: AsyncClient, admin_headers):
    """测试创建知识库"""
    resp = await client.post(
        "/api/knowledge-bases",
        json={"name": "测试新建知识库", "description": "测试描述"},
        headers=admin_headers,
    )
    assert resp.status_code == 201
    data = resp.json()
    assert data["name"] == "测试新建知识库"
    assert "id" in data


@pytest.mark.asyncio
async def test_get_knowledge_base_detail(client: AsyncClient, admin_headers):
    """测试获取知识库详情"""
    # 先创建
    create_resp = await client.post(
        "/api/knowledge-bases",
        json={"name": "详情测试库"},
        headers=admin_headers,
    )
    kb_id = create_resp.json()["id"]

    resp = await client.get(f"/api/knowledge-bases/{kb_id}", headers=admin_headers)
    assert resp.status_code == 200
    assert resp.json()["name"] == "详情测试库"


@pytest.mark.asyncio
async def test_get_knowledge_base_not_found(client: AsyncClient, admin_headers):
    """测试获取不存在的知识库"""
    resp = await client.get(
        "/api/knowledge-bases/nonexistent-id-12345",
        headers=admin_headers,
    )
    assert resp.status_code == 404


@pytest.mark.asyncio
async def test_update_knowledge_base(client: AsyncClient, admin_headers):
    """测试更新知识库"""
    create_resp = await client.post(
        "/api/knowledge-bases",
        json={"name": "更新前"},
        headers=admin_headers,
    )
    kb_id = create_resp.json()["id"]

    resp = await client.put(
        f"/api/knowledge-bases/{kb_id}",
        json={"name": "更新后", "description": "新描述"},
        headers=admin_headers,
    )
    assert resp.status_code == 200
    assert resp.json()["name"] == "更新后"


@pytest.mark.asyncio
async def test_delete_knowledge_base(client: AsyncClient, admin_headers):
    """测试删除知识库"""
    create_resp = await client.post(
        "/api/knowledge-bases",
        json={"name": "待删除"},
        headers=admin_headers,
    )
    kb_id = create_resp.json()["id"]

    resp = await client.delete(f"/api/knowledge-bases/{kb_id}", headers=admin_headers)
    assert resp.status_code == 204


@pytest.mark.asyncio
async def test_kb_detail_requires_auth(client: AsyncClient):
    """测试知识库详情需要登录"""
    resp = await client.get("/api/knowledge-bases/some-id")
    assert resp.status_code == 401

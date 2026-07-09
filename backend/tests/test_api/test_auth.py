"""认证 API 测试"""
import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_health_check(client: AsyncClient):
    """测试健康检查"""
    resp = await client.get("/health")
    assert resp.status_code == 200
    assert resp.json()["status"] == "ok"


@pytest.mark.asyncio
async def test_root_endpoint(client: AsyncClient):
    """测试根路径"""
    resp = await client.get("/")
    assert resp.status_code == 200
    data = resp.json()
    assert "知识问答系统" in data["message"]


@pytest.mark.asyncio
async def test_register_success(client: AsyncClient):
    """测试用户注册成功"""
    resp = await client.post("/api/auth/register", json={
        "username": "test_register_user",
        "email": "test_register@example.com",
        "password": "test123456",
        "nickname": "测试用户",
    })
    assert resp.status_code == 201
    data = resp.json()
    assert "access_token" in data
    assert data["user"]["username"] == "test_register_user"


@pytest.mark.asyncio
async def test_register_duplicate_username(client: AsyncClient):
    """测试重复用户名注册"""
    # 先注册一个用户
    await client.post("/api/auth/register", json={
        "username": "dup_user",
        "email": "dup1@example.com",
        "password": "test123456",
    })
    # 再用相同用户名注册
    resp = await client.post("/api/auth/register", json={
        "username": "dup_user",
        "email": "dup2@example.com",
        "password": "test123456",
    })
    assert resp.status_code == 422


@pytest.mark.asyncio
async def test_login_success(client: AsyncClient):
    """测试登录成功"""
    resp = await client.post("/api/auth/login", json={
        "username": "admin",
        "password": "admin123",
    })
    assert resp.status_code == 200
    data = resp.json()
    assert "access_token" in data
    assert data["user"]["role"] == "admin"


@pytest.mark.asyncio
async def test_login_wrong_password(client: AsyncClient):
    """测试错误密码登录"""
    resp = await client.post("/api/auth/login", json={
        "username": "admin",
        "password": "wrong_password",
    })
    assert resp.status_code == 422


@pytest.mark.asyncio
async def test_login_nonexistent_user(client: AsyncClient):
    """测试不存在的用户登录"""
    resp = await client.post("/api/auth/login", json={
        "username": "nonexistent_user_12345",
        "password": "test123456",
    })
    assert resp.status_code == 422


@pytest.mark.asyncio
async def test_get_me(client: AsyncClient):
    """测试获取当前用户"""
    # 先登录获取 token
    login_resp = await client.post("/api/auth/login", json={
        "username": "admin",
        "password": "admin123",
    })
    token = login_resp.json()["access_token"]

    # 获取用户信息
    resp = await client.get("/api/auth/me", headers={"Authorization": f"Bearer {token}"})
    assert resp.status_code == 200
    data = resp.json()
    assert data["username"] == "admin"
    assert data["role"] == "admin"


@pytest.mark.asyncio
async def test_get_me_no_token(client: AsyncClient):
    """测试未登录获取用户信息"""
    resp = await client.get("/api/auth/me")
    assert resp.status_code == 401


@pytest.mark.asyncio
async def test_get_me_invalid_token(client: AsyncClient):
    """测试无效 token 获取用户信息"""
    resp = await client.get("/api/auth/me", headers={"Authorization": "Bearer invalid_token"})
    assert resp.status_code == 401


@pytest.mark.asyncio
async def test_update_profile(client: AsyncClient):
    """测试更新个人信息"""
    login_resp = await client.post("/api/auth/login", json={
        "username": "admin",
        "password": "admin123",
    })
    token = login_resp.json()["access_token"]

    resp = await client.put(
        "/api/auth/me",
        json={"nickname": "新昵称"},
        headers={"Authorization": f"Bearer {token}"},
    )
    assert resp.status_code == 200
    assert resp.json()["nickname"] == "新昵称"


@pytest.mark.asyncio
async def test_change_password(client: AsyncClient):
    """测试修改密码"""
    # 注册新用户
    reg_resp = await client.post("/api/auth/register", json={
        "username": "pwd_test_user",
        "email": "pwd_test@example.com",
        "password": "old_pass_123",
    })
    token = reg_resp.json()["access_token"]

    # 修改密码
    resp = await client.put(
        "/api/auth/password",
        json={"old_password": "old_pass_123", "new_password": "new_pass_456"},
        headers={"Authorization": f"Bearer {token}"},
    )
    assert resp.status_code == 200

    # 用新密码登录
    login_resp = await client.post("/api/auth/login", json={
        "username": "pwd_test_user",
        "password": "new_pass_456",
    })
    assert login_resp.status_code == 200


@pytest.mark.asyncio
async def test_change_password_wrong_old(client: AsyncClient):
    """测试错误旧密码修改"""
    reg_resp = await client.post("/api/auth/register", json={
        "username": "pwd_wrong_user",
        "email": "pwd_wrong@example.com",
        "password": "correct_pass",
    })
    token = reg_resp.json()["access_token"]

    resp = await client.put(
        "/api/auth/password",
        json={"old_password": "wrong_pass", "new_password": "new_pass"},
        headers={"Authorization": f"Bearer {token}"},
    )
    assert resp.status_code == 422

"""全面功能测试脚本"""
import httpx
import json
import time

BASE_URL = "http://localhost:8000"
results = []

def test(name, func):
    """执行测试并记录结果"""
    try:
        result = func()
        results.append({"name": name, "status": "PASS", "detail": result})
        print(f"  ✅ {name}: {result}")
    except Exception as e:
        results.append({"name": name, "status": "FAIL", "detail": str(e)})
        print(f"  ❌ {name}: {str(e)[:80]}")

def main():
    print("=" * 60)
    print("知识问答系统 - 全面功能测试")
    print("=" * 60)
    print()

    # 创建客户端
    client = httpx.Client(base_url=BASE_URL, timeout=30)

    # ==================== 认证模块 ====================
    print("【认证模块】")

    def test_register():
        r = client.post("/api/auth/register", json={
            "username": "test_user",
            "email": "test@example.com",
            "password": "test123",
            "nickname": "测试用户"
        })
        if r.status_code == 201:
            return "注册成功"
        elif "已存在" in r.text:
            return "用户已存在（跳过）"
        else:
            raise Exception(f"状态码: {r.status_code}")

    test("用户注册", test_register)

    def test_login():
        r = client.post("/api/auth/login", json={
            "username": "admin",
            "password": "admin123"
        })
        data = r.json()
        client.headers["Authorization"] = f"Bearer {data['access_token']}"
        return f"登录成功, 角色: {data['user']['role']}"

    test("管理员登录", test_login)

    def test_get_me():
        r = client.get("/api/auth/me")
        data = r.json()
        return f"用户名: {data['username']}, 角色: {data['role']}"

    test("获取当前用户", test_get_me)

    def test_update_profile():
        r = client.put("/api/auth/me", json={"nickname": "超级管理员"})
        return f"昵称更新为: {r.json()['nickname']}"

    test("更新个人信息", test_update_profile)

    print()

    # ==================== 知识库模块 ====================
    print("【知识库模块】")

    def test_list_my_kb():
        r = client.get("/api/knowledge-bases/my")
        data = r.json()
        return f"共 {data['total']} 个知识库"

    test("获取我的知识库", test_list_my_kb)

    def test_marketplace():
        r = client.get("/api/knowledge-bases/marketplace")
        data = r.json()
        return f"共 {data['total']} 个公开知识库"

    test("获取知识库广场", test_marketplace)

    test_kb_id = None

    def test_create_kb():
        nonlocal test_kb_id
        r = client.post("/api/knowledge-bases", json={
            "name": "功能测试知识库",
            "description": "用于测试的知识库",
            "is_public": True
        })
        data = r.json()
        test_kb_id = data["id"]
        return f"ID: {test_kb_id[:8]}..."

    test("创建知识库", test_create_kb)

    def test_get_kb():
        r = client.get(f"/api/knowledge-bases/{test_kb_id}")
        return f"名称: {r.json()['name']}"

    test("获取知识库详情", test_get_kb)

    def test_update_kb():
        r = client.put(f"/api/knowledge-bases/{test_kb_id}", json={
            "description": "更新后的描述"
        })
        return f"描述: {r.json()['description']}"

    test("更新知识库", test_update_kb)

    def test_upload_doc():
        content = "# 测试文档\n\n这是一个测试文档。"
        files = {"file": ("test.md", content.encode(), "text/markdown")}
        r = client.post(f"/api/knowledge-bases/{test_kb_id}/documents/upload", files=files)
        return f"状态码: {r.status_code}"

    test("上传文档", test_upload_doc)

    def test_list_docs():
        r = client.get(f"/api/knowledge-bases/{test_kb_id}/documents")
        return f"共 {len(r.json())} 个文档"

    test("获取文档列表", test_list_docs)

    print()

    # ==================== 聊天模块 ====================
    print("【聊天模块】")

    conv_id = None

    def test_create_conv():
        nonlocal conv_id
        r = client.post("/api/conversations", json={
            "knowledge_base_id": "dab30740-a3ed-4609-a073-978a6b2cf4d8",
            "title": "测试对话"
        })
        data = r.json()
        conv_id = data["id"]
        return f"ID: {conv_id[:8]}..."

    test("创建对话", test_create_conv)

    def test_list_convs():
        r = client.get("/api/conversations")
        return f"共 {len(r.json())} 个对话"

    test("获取对话列表", test_list_convs)

    def test_chat():
        r = client.post("/api/chat", json={
            "knowledge_base_id": "dab30740-a3ed-4609-a073-978a6b2cf4d8",
            "conversation_id": conv_id,
            "message": "Python是什么？",
            "stream": False
        })
        data = r.json()
        return f"回答长度: {len(data.get('content', ''))} 字符"

    test("发送消息", test_chat)

    def test_list_msgs():
        r = client.get(f"/api/conversations/{conv_id}/messages")
        return f"共 {len(r.json())} 条消息"

    test("获取消息历史", test_list_msgs)

    def test_export():
        r = client.get(f"/api/conversations/{conv_id}/export?format=markdown")
        return f"导出成功, 长度: {len(r.text)} 字符"

    test("导出对话", test_export)

    print()

    # ==================== 反馈模块 ====================
    print("【反馈模块】")

    def test_feedback():
        r = client.post("/api/feedback", json={
            "message_id": "test-msg-id",
            "conversation_id": conv_id,
            "rating": 5,
            "comment": "测试反馈"
        })
        return f"状态码: {r.status_code}"

    test("提交反馈", test_feedback)

    print()

    # ==================== 帮助模块 ====================
    print("【帮助模块】")

    def test_help_list():
        r = client.get("/api/help")
        return f"共 {len(r.json())} 个分类"

    test("获取帮助分类", test_help_list)

    def test_help_search():
        r = client.get("/api/help/search?q=文档")
        return f"找到 {r.json()['total']} 条结果"

    test("搜索帮助内容", test_help_search)

    print()

    # ==================== 管理后台模块 ====================
    print("【管理后台模块】")

    def test_admin_users():
        r = client.get("/api/admin/users")
        return f"共 {len(r.json())} 个用户"

    test("获取用户列表", test_admin_users)

    def test_admin_kbs():
        r = client.get("/api/admin/knowledge-bases")
        return f"共 {r.json()['total']} 个知识库"

    test("获取所有知识库", test_admin_kbs)

    def test_admin_docs():
        r = client.get("/api/admin/documents")
        return f"共 {len(r.json())} 个文档"

    test("获取所有文档", test_admin_docs)

    def test_admin_stats():
        r = client.get("/api/admin/stats/overview")
        data = r.json()
        return f"用户:{data['user_count']} KB:{data['knowledge_base_count']} 文档:{data['document_count']}"

    test("获取统计数据", test_admin_stats)

    def test_admin_settings():
        r = client.get("/api/admin/settings")
        return f"LLM: {r.json()['llm']['provider']}"

    test("获取系统设置", test_admin_settings)

    def test_settings():
        r = client.get("/api/settings")
        return f"LLM: {r.json()['llm']['provider']}"

    test("获取公开设置", test_settings)

    print()

    # ==================== 清理测试数据 ====================
    print("【清理测试数据】")

    def test_delete_kb():
        if test_kb_id:
            r = client.delete(f"/api/knowledge-bases/{test_kb_id}")
            return f"状态码: {r.status_code}"
        return "跳过"

    test("删除测试知识库", test_delete_kb)

    def test_delete_conv():
        if conv_id:
            r = client.delete(f"/api/conversations/{conv_id}")
            return f"状态码: {r.status_code}"
        return "跳过"

    test("删除测试对话", test_delete_conv)

    print()

    # ==================== 测试总结 ====================
    print("=" * 60)
    print("测试总结")
    print("=" * 60)

    passed = sum(1 for r in results if r["status"] == "PASS")
    failed = sum(1 for r in results if r["status"] == "FAIL")
    total = len(results)

    print(f"总数: {total}")
    print(f"通过: {passed}")
    print(f"失败: {failed}")
    print(f"通过率: {passed/total*100:.1f}%")

    if failed > 0:
        print()
        print("失败项:")
        for r in results:
            if r["status"] == "FAIL":
                print(f"  - {r['name']}: {r['detail']}")

    print()
    print("=" * 60)


if __name__ == "__main__":
    main()

"""安全过滤测试"""
from app.services.chat import check_sensitive_content, filter_response


class TestSecurity:
    """内容安全过滤测试"""

    def test_check_safe_content(self):
        """测试安全内容"""
        is_safe, msg = check_sensitive_content("Python 是什么？")
        assert is_safe is True

    def test_check_sensitive_content(self):
        """测试敏感内容"""
        is_safe, msg = check_sensitive_content("如何参与赌博")
        assert is_safe is False
        assert "敏感词" in msg

    def test_filter_response_safe(self):
        """测试过滤安全内容"""
        result = filter_response("这是一个正常回答")
        assert result == "这是一个正常回答"

    def test_filter_response_sensitive(self):
        """测试过滤敏感内容"""
        result = filter_response("这里提到了赌博内容")
        assert "***" in result
        assert "赌博" not in result

    def test_empty_content(self):
        """测试空内容"""
        is_safe, msg = check_sensitive_content("")
        assert is_safe is True

        result = filter_response("")
        assert result == ""

"""
Tests for AI Service - JSON extraction and utilities
"""
import pytest
import json
from app.services.ai_service import extract_json_from_response, is_ai_enabled


class TestExtractJsonFromResponse:
    """Test cases for extract_json_from_response()"""
    
    def test_clean_json(self):
        """Direct JSON should parse correctly"""
        result = extract_json_from_response('{"key": "value", "count": 42}')
        assert result == {"key": "value", "count": 42}
    
    def test_json_with_whitespace(self):
        """JSON with leading/trailing whitespace"""
        result = extract_json_from_response('  \n{"key": "value"}\n  ')
        assert result == {"key": "value"}
    
    def test_markdown_json_block(self):
        """JSON wrapped in markdown code block"""
        text = '```json\n{"faqs": [{"q": "What?", "a": "This."}]}\n```'
        result = extract_json_from_response(text)
        assert result == {"faqs": [{"q": "What?", "a": "This."}]}
    
    def test_markdown_block_no_language(self):
        """Markdown code block without language specifier"""
        text = '```\n{"key": "value"}\n```'
        result = extract_json_from_response(text)
        assert result == {"key": "value"}
    
    def test_json_with_surrounding_text(self):
        """JSON embedded in explanatory text"""
        text = 'Here is your result:\n\n{"title": "Test", "score": 85}\n\nHope this helps!'
        result = extract_json_from_response(text)
        assert result == {"title": "Test", "score": 85}
    
    def test_nested_json(self):
        """Nested JSON structures"""
        data = {
            "article": {
                "title": "Test",
                "sections": [{"heading": "Intro"}, {"heading": "Body"}]
            },
            "meta": {"words": 500}
        }
        result = extract_json_from_response(json.dumps(data))
        assert result == data
    
    def test_json_with_special_chars(self):
        """JSON with special characters in strings"""
        text = '{"content": "Line 1\\nLine 2", "quote": "He said \\"hello\\""}'
        result = extract_json_from_response(text)
        assert result["content"] == "Line 1\nLine 2"
        assert result["quote"] == 'He said "hello"'
    
    def test_invalid_json_raises(self):
        """Invalid JSON should raise JSONDecodeError"""
        with pytest.raises(json.JSONDecodeError):
            extract_json_from_response("This is not JSON at all")
    
    def test_malformed_json_raises(self):
        """Malformed JSON should raise JSONDecodeError"""
        with pytest.raises(json.JSONDecodeError):
            extract_json_from_response('{"key": value}')  # unquoted value
    
    def test_empty_string_raises(self):
        """Empty string should raise JSONDecodeError"""
        with pytest.raises(json.JSONDecodeError):
            extract_json_from_response("")
    
    def test_array_json(self):
        """JSON array (not object) - should work with {...} extraction fallback"""
        # Note: Current implementation extracts first {...} block,
        # so arrays at top level may not work. This test documents behavior.
        text = '[{"a": 1}, {"b": 2}]'
        result = extract_json_from_response(text)
        # Should parse the full array if direct parse works
        assert result == [{"a": 1}, {"b": 2}]


class TestIsAiEnabled:
    """Test AI availability check"""
    
    def test_returns_bool(self):
        """is_ai_enabled should return a boolean"""
        result = is_ai_enabled()
        assert isinstance(result, bool)


# Run with: pytest tests/test_ai_service.py -v

from unittest.mock import patch, MagicMock
from config.llm import get_llm


def test_get_llm_returns_anthropic_when_api_key_set(monkeypatch):
    monkeypatch.setenv("ANTHROPIC_API_KEY", "sk-ant-test-key")
    with patch("config.llm.ChatAnthropic") as mock_cls:
        mock_cls.return_value = MagicMock()
        result = get_llm()
    mock_cls.assert_called_once_with(
        model_name="claude-sonnet-4-6",
        api_key="sk-ant-test-key",
        timeout=180,
        max_retries=3,
        stop=["\n\nHuman:", "\n\nAssistant:"],
    )
    assert result is mock_cls.return_value


def test_get_llm_returns_ollama_when_no_api_key(monkeypatch):
    monkeypatch.delenv("ANTHROPIC_API_KEY", raising=False)
    with patch("config.llm.ChatOllama") as mock_cls:
        mock_cls.return_value = MagicMock()
        result = get_llm()
    mock_cls.assert_called_once_with(model="gemma4:26b", base_url="http://localhost:11434")
    assert result is mock_cls.return_value


def test_get_llm_respects_custom_ollama_env_vars(monkeypatch):
    monkeypatch.delenv("ANTHROPIC_API_KEY", raising=False)
    monkeypatch.setenv("OLLAMA_MODEL", "mistral")
    monkeypatch.setenv("OLLAMA_BASE_URL", "http://my-server:11434")
    with patch("config.llm.ChatOllama") as mock_cls:
        mock_cls.return_value = MagicMock()
        get_llm()
    mock_cls.assert_called_once_with(model="mistral", base_url="http://my-server:11434")

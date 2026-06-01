from unittest.mock import MagicMock, patch

import pytest

from src.adapters.llm_analyzer import AnalysisError, LLMAnalyzerAdapter
from src.core.models import LLMAnalysisResult


def test_no_api_key():
    with patch.dict("os.environ", {}, clear=True):
        with pytest.raises(AnalysisError, match="OPENAI_API_KEY not set"):
            LLMAnalyzerAdapter()


@patch("src.adapters.llm_analyzer.OpenAI")
def test_analyze_success(mock_openai):
    mock_client = MagicMock()
    mock_openai.return_value = mock_client
    mock_client.chat.completions.create.return_value.choices[0].message.content = (
        "### 1. Common Verb Tenses\n* Present Simple: \"I like coffee\" — ..."
    )

    adapter = LLMAnalyzerAdapter(api_key="test-key", model="gpt-4o-mini")
    result = adapter.analyze("Hello world")

    assert isinstance(result, LLMAnalysisResult)
    assert "Common Verb Tenses" in result.markdown
    mock_client.chat.completions.create.assert_called_once()


@patch("src.adapters.llm_analyzer.OpenAI")
def test_analyze_empty_response(mock_openai):
    mock_client = MagicMock()
    mock_openai.return_value = mock_client
    mock_client.chat.completions.create.return_value.choices[0].message.content = ""

    adapter = LLMAnalyzerAdapter(api_key="test-key")
    result = adapter.analyze("Hello world")

    assert result.markdown == ""


@patch("src.adapters.llm_analyzer.OpenAI")
def test_analyze_api_error(mock_openai):
    mock_client = MagicMock()
    mock_openai.return_value = mock_client
    mock_client.chat.completions.create.side_effect = Exception("API error")

    adapter = LLMAnalyzerAdapter(api_key="test-key")
    with pytest.raises(AnalysisError, match="LLM analysis failed"):
        adapter.analyze("Hello world")

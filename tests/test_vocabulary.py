import pytest

from src.core.models import VocabularyResult
from src.core.vocabulary import VocabularyAnalyzer


@pytest.fixture
def analyzer():
    return VocabularyAnalyzer()


def test_extract_word_freq(analyzer):
    text = "hello world hello everyone hello"
    result = analyzer.extract(text, top_n=10)

    assert isinstance(result, VocabularyResult)
    assert len(result.word_freq) > 0

    words = dict(result.word_freq)
    assert "hello" in words
    assert words["hello"] >= 3


def test_extract_lemma_freq(analyzer):
    text = "running runs ran runner"
    result = analyzer.extract(text, top_n=10)

    assert isinstance(result, VocabularyResult)
    lemmas = dict(result.lemma_freq)
    assert "run" in lemmas


def test_empty_text(analyzer):
    result = analyzer.extract("", top_n=10)
    assert isinstance(result, VocabularyResult)
    assert len(result.word_freq) == 0

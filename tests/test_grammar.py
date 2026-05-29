import pytest

from src.analysis.grammar import GrammarAnalyzer, GrammarResult


@pytest.fixture
def analyzer():
    return GrammarAnalyzer()


def test_extract_pos_patterns(analyzer):
    text = "I like coffee. She likes tea."
    result = analyzer.extract(text, top_n=10)

    assert isinstance(result, GrammarResult)
    assert len(result.pos_patterns) > 0

    pattern, example, count = result.pos_patterns[0]
    assert isinstance(pattern, str)
    assert isinstance(example, str)
    assert isinstance(count, int)


def test_extract_dep_triples(analyzer):
    text = "The cat sat on the mat."
    result = analyzer.extract(text, top_n=10)

    assert isinstance(result, GrammarResult)
    assert len(result.dep_triples) > 0

    triple, count = result.dep_triples[0]
    assert isinstance(triple, str)
    assert isinstance(count, int)


def test_empty_text(analyzer):
    result = analyzer.extract("", top_n=10)
    assert isinstance(result, GrammarResult)
    assert len(result.pos_patterns) == 0

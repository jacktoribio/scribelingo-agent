from src.core.models import PhrasesResult
from src.core.phrases import PhraseAnalyzer


def test_extract_ngrams():
    text = "I really enjoy learning English. Learning English every day is fun. Learning English helps me grow."
    analyzer = PhraseAnalyzer(min_freq=1)
    result = analyzer.extract(text, ngram_range=(2, 3), top_n=10)

    assert isinstance(result, PhrasesResult)
    assert 2 in result.ngrams
    assert 3 in result.ngrams

    bigrams = dict(result.ngrams[2])
    assert "learning english" in bigrams
    assert bigrams["learning english"] >= 2


def test_extract_collocations():
    text = "I really enjoy learning English every single day without fail."
    analyzer = PhraseAnalyzer(min_freq=1)
    result = analyzer.extract(text, top_n=10)

    assert isinstance(result.collocations, list)
    if result.collocations:
        phrase, score = result.collocations[0]
        assert isinstance(phrase, tuple)
        assert isinstance(score, float)


def test_empty_text():
    analyzer = PhraseAnalyzer(min_freq=1)
    result = analyzer.extract("", top_n=10)

    assert isinstance(result, PhrasesResult)
    assert all(len(v) == 0 for v in result.ngrams.values())

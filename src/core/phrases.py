from collections import Counter
from math import log2
from typing import Tuple

from nltk import ngrams
from nltk.collocations import BigramAssocMeasures, BigramCollocationFinder
from nltk.tokenize import word_tokenize

from src.core.models import PhrasesResult
from src.utils.helpers import STOPWORDS_EN


class PhraseAnalyzer:
    def __init__(self, min_freq: int = 2):
        self.min_freq = min_freq

    def extract(
        self,
        text: str,
        ngram_range: Tuple[int, int] = (2, 5),
        top_n: int = 50,
    ) -> PhrasesResult:
        tokens = word_tokenize(text.lower())
        tokens = [
            t for t in tokens
            if t.isalpha() and t not in STOPWORDS_EN
        ]

        result = PhrasesResult()

        for n in range(ngram_range[0], ngram_range[1] + 1):
            ngram_counts = Counter(" ".join(ng) for ng in ngrams(tokens, n))
            ranked = sorted(
                ngram_counts.items(),
                key=lambda x: x[1],
                reverse=True,
            )
            filtered = [(p, c) for p, c in ranked if c >= self.min_freq]
            result.ngrams[n] = filtered[:top_n]

        if len(tokens) >= 2:
            finder = BigramCollocationFinder.from_words(tokens)
            finder.apply_freq_filter(self.min_freq)
            scored = finder.score_ngrams(BigramAssocMeasures.pmi)
            result.collocations = sorted(
                scored, key=lambda x: x[1], reverse=True
            )[:top_n]

        return result

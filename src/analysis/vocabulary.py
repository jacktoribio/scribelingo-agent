from collections import Counter
from dataclasses import dataclass, field
from typing import List, Tuple

import spacy
from sklearn.feature_extraction.text import TfidfVectorizer

from src.utils.helpers import STOPWORDS_EN


@dataclass
class VocabularyResult:
    word_freq: List[Tuple[str, int]] = field(default_factory=list)
    lemma_freq: List[Tuple[str, int]] = field(default_factory=list)
    keywords: List[Tuple[str, float]] = field(default_factory=list)


class VocabularyAnalyzer:
    def __init__(self):
        self._nlp = spacy.load("en_core_web_sm")

    def extract(self, text: str, top_n: int = 50) -> VocabularyResult:
        doc = self._nlp(text.lower())

        word_counts: Counter = Counter()
        lemma_counts: Counter = Counter()

        for token in doc:
            if (
                token.is_alpha
                and not token.is_stop
                and token.text not in STOPWORDS_EN
            ):
                word_counts[token.text] += 1
                lemma_counts[token.lemma_] += 1

        result = VocabularyResult(
            word_freq=word_counts.most_common(top_n),
            lemma_freq=lemma_counts.most_common(top_n),
        )

        sentences = [sent.text for sent in doc.sents]
        if len(sentences) >= 2:
            try:
                vectorizer = TfidfVectorizer(
                    stop_words=list(STOPWORDS_EN),
                    max_features=top_n,
                )
                tfidf_matrix = vectorizer.fit_transform(sentences)
                feature_names = vectorizer.get_feature_names_out()
                scores = tfidf_matrix.sum(axis=0).tolist()[0]
                ranked = sorted(
                    zip(feature_names, scores),
                    key=lambda x: x[1],
                    reverse=True,
                )
                result.keywords = ranked[:top_n]
            except ValueError:
                pass

        return result

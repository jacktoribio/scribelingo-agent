from collections import Counter
from typing import List, Tuple

import spacy
from spacy.tokens import Doc

from src.core.models import GrammarResult


class GrammarAnalyzer:
    def __init__(self):
        self._nlp = spacy.load("en_core_web_sm")

    def extract(self, text: str, top_n: int = 30) -> GrammarResult:
        doc: Doc = self._nlp(text)

        pos_counts: Counter = Counter()
        dep_counts: Counter = Counter()

        for sent in doc.sents:
            tags = [token.tag_ for token in sent if not token.is_punct]
            if len(tags) >= 2:
                pattern = " ".join(tags)
                pos_counts[pattern] += 1

        for token in doc:
            if token.dep_ != "ROOT" and token.head.pos_ != "PUNCT":
                triple = f"{token.dep_}({token.head.lemma_}, {token.lemma_})"
                dep_counts[triple] += 1

        top_pos = pos_counts.most_common(top_n)
        top_dep = dep_counts.most_common(top_n)

        result = GrammarResult()
        for pattern, count in top_pos:
            example = self._find_example(doc, pattern)
            result.pos_patterns.append((pattern, example, count))

        for triple, count in top_dep:
            result.dep_triples.append((triple, count))

        return result

    def _find_example(self, doc: Doc, target_pattern: str) -> str:
        for sent in doc.sents:
            tags = [token.tag_ for token in sent if not token.is_punct]
            if len(tags) >= 2:
                pattern = " ".join(tags)
                if pattern == target_pattern:
                    return sent.text.strip()
        return ""

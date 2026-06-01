from dataclasses import dataclass, field
from typing import Dict, List, Tuple


@dataclass
class TranscriptionResult:
    text: str
    segments: List[dict] = field(default_factory=list)
    language: str = ""


@dataclass
class LLMAnalysisResult:
    markdown: str = ""


@dataclass
class PhrasesResult:
    ngrams: Dict[int, List[Tuple[str, float]]] = field(default_factory=dict)
    collocations: List[Tuple[str, float]] = field(default_factory=list)


@dataclass
class GrammarResult:
    pos_patterns: List[Tuple[str, str, int]] = field(default_factory=list)
    dep_triples: List[Tuple[str, int]] = field(default_factory=list)


@dataclass
class VocabularyResult:
    word_freq: List[Tuple[str, int]] = field(default_factory=list)
    lemma_freq: List[Tuple[str, int]] = field(default_factory=list)
    keywords: List[Tuple[str, float]] = field(default_factory=list)

from abc import ABC, abstractmethod
from pathlib import Path

from src.core.models import (
    GrammarResult,
    LLMAnalysisResult,
    PhrasesResult,
    TranscriptionResult,
    VocabularyResult,
)


class AudioExtractorPort(ABC):
    @abstractmethod
    def extract_audio(
        self, video_path: Path, audio_path: Path | None = None
    ) -> Path:
        ...


class TranscriberPort(ABC):
    @abstractmethod
    def transcribe(self, audio_path: Path) -> TranscriptionResult:
        ...


class AnalyzerPort(ABC):
    @abstractmethod
    def analyze(self, text: str) -> LLMAnalysisResult:
        ...


class ReportGeneratorPort(ABC):
    @abstractmethod
    def generate(
        self,
        transcript: str,
        phrases: PhrasesResult,
        grammar: GrammarResult,
        vocabulary: VocabularyResult,
        output_path: Path,
        format: str = "html",
    ) -> Path:
        ...

from pathlib import Path
import re
from typing import List

SUPPORTED_VIDEO_FORMATS = {".mp4", ".avi", ".mov", ".mkv", ".webm"}
SUPPORTED_AUDIO_FORMATS = {".wav", ".mp3", ".m4a", ".flac"}
STOPWORDS_EN = frozenset({
    "a", "an", "the", "and", "or", "but", "in", "on", "at", "to",
    "for", "of", "with", "by", "from", "is", "are", "was", "were",
    "be", "been", "being", "have", "has", "had", "do", "does", "did",
    "will", "would", "could", "should", "may", "might", "shall",
    "can", "i", "you", "he", "she", "it", "we", "they",
    "me", "him", "her", "us", "them", "my", "your", "his", "its",
    "our", "their", "this", "that", "these", "those",
    "not", "no", "nor", "so", "very", "just", "about",
})


def validate_video_file(path: Path) -> Path:
    path = Path(path).resolve()
    if not path.exists():
        raise FileNotFoundError(f"Video file not found: {path}")
    if path.suffix.lower() not in SUPPORTED_VIDEO_FORMATS:
        raise ValueError(
            f"Unsupported video format: {path.suffix}. "
            f"Supported: {SUPPORTED_VIDEO_FORMATS}"
        )
    return path


def validate_audio_file(path: Path) -> Path:
    path = Path(path).resolve()
    if not path.exists():
        raise FileNotFoundError(f"Audio file not found: {path}")
    if path.suffix.lower() not in SUPPORTED_AUDIO_FORMATS:
        raise ValueError(
            f"Unsupported audio format: {path.suffix}. "
            f"Supported: {SUPPORTED_AUDIO_FORMATS}"
        )
    return path


def clean_text(text: str) -> str:
    text = text.lower()
    text = re.sub(r"[^a-z0-9\s'.,!?]", "", text)
    text = re.sub(r"\s+", " ", text).strip()
    return text


def tokenize_words(text: str) -> List[str]:
    return re.findall(r"\b[a-z']+\b", clean_text(text))

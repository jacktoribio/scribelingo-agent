from pathlib import Path
from typing import Optional

import whisper

from src.core.models import TranscriptionResult
from src.core.ports import TranscriberPort


class TranscriptionError(Exception):
    pass


class LocalWhisperAdapter(TranscriberPort):
    def __init__(self, model_size: str = "base"):
        self.model_size = model_size
        self._model: Optional[whisper.Whisper] = None

    def _load_model(self) -> None:
        if self._model is None:
            self._model = whisper.load_model(self.model_size)

    def transcribe(self, audio_path: Path) -> TranscriptionResult:
        audio_path = Path(audio_path).resolve()
        if not audio_path.exists():
            raise FileNotFoundError(f"Audio not found: {audio_path}")

        self._load_model()

        try:
            result = self._model.transcribe(
                str(audio_path),
                fp16=False,
                task="transcribe",
            )
        except Exception as exc:
            raise TranscriptionError(
                f"Whisper transcription failed: {exc}"
            ) from exc

        return TranscriptionResult(
            text=result.get("text", "").strip(),
            segments=result.get("segments", []),
            language=result.get("language", ""),
        )

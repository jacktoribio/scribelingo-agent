import os
import tempfile
from pathlib import Path

from openai import OpenAI
from pydub import AudioSegment

from src.core.models import TranscriptionResult
from src.core.ports import TranscriberPort

MAX_FILE_BYTES = 20 * 1024 * 1024


class TranscriptionError(Exception):
    pass


class OpenAIAPIAdapter(TranscriberPort):
    def __init__(self, api_key: str | None = None, model: str = "whisper-1"):
        self.api_key = api_key or os.getenv("OPENAI_API_KEY")
        if not self.api_key:
            raise TranscriptionError(
                "OPENAI_API_KEY not set. Provide api_key or set the "
                "OPENAI_API_KEY environment variable."
            )
        self.model = model
        self._client: OpenAI | None = None

    @property
    def client(self) -> OpenAI:
        if self._client is None:
            self._client = OpenAI(api_key=self.api_key)
        return self._client

    def transcribe(self, audio_path: Path) -> TranscriptionResult:
        audio_path = Path(audio_path).resolve()
        if not audio_path.exists():
            raise FileNotFoundError(f"Audio not found: {audio_path}")

        file_size = audio_path.stat().st_size
        if file_size <= MAX_FILE_BYTES:
            return self._transcribe_file(audio_path)

        return self._transcribe_split(audio_path)

    def _transcribe_file(self, audio_path: Path) -> TranscriptionResult:
        try:
            with open(audio_path, "rb") as audio_file:
                response = self.client.audio.transcriptions.create(
                    model=self.model,
                    file=audio_file,
                    response_format="verbose_json",
                )
        except Exception as exc:
            raise TranscriptionError(
                f"OpenAI transcription failed: {exc}"
            ) from exc

        return self._parse_response(response)

    def _transcribe_split(self, audio_path: Path) -> TranscriptionResult:
        audio = AudioSegment.from_file(str(audio_path))
        total_ms = len(audio)
        bytes_per_ms = audio_path.stat().st_size / total_ms if total_ms else 1
        chunk_duration_ms = int(MAX_FILE_BYTES / bytes_per_ms * 0.9)
        chunk_duration_ms = max(chunk_duration_ms, 30_000)

        text_parts: list[str] = []
        all_segments: list[dict] = []
        language = ""

        with tempfile.TemporaryDirectory() as tmp_dir:
            for start_ms in range(0, total_ms, chunk_duration_ms):
                end_ms = min(start_ms + chunk_duration_ms, total_ms)
                chunk = audio[start_ms:end_ms]

                chunk_path = Path(tmp_dir) / f"chunk_{start_ms}.wav"
                chunk.export(str(chunk_path), format="wav")

                result = self._transcribe_file(chunk_path)
                text_parts.append(result.text)

                offset_sec = start_ms / 1000
                for seg in result.segments:
                    seg["start"] = round(seg.get("start", 0) + offset_sec, 2)
                    seg["end"] = round(seg.get("end", 0) + offset_sec, 2)
                    all_segments.append(seg)

                if not language and result.language:
                    language = result.language

        return TranscriptionResult(
            text=" ".join(text_parts).strip(),
            segments=all_segments,
            language=language,
        )

    def _parse_response(self, response) -> TranscriptionResult:
        segments: list[dict] = []
        if hasattr(response, "segments") and response.segments:
            for seg in response.segments:
                segments.append({
                    "start": getattr(seg, "start", 0),
                    "end": getattr(seg, "end", 0),
                    "text": getattr(seg, "text", ""),
                })

        return TranscriptionResult(
            text=getattr(response, "text", "").strip(),
            segments=segments,
            language=getattr(response, "language", "") or "",
        )

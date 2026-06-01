from pathlib import Path
from unittest.mock import patch

import pytest

from src.adapters.local_transcriber import LocalWhisperAdapter
from src.core.models import TranscriptionResult


def test_transcribe_file_not_found():
    transcriber = LocalWhisperAdapter(model_size="tiny")
    with pytest.raises(FileNotFoundError):
        transcriber.transcribe(Path("nonexistent.wav"))


@patch("src.adapters.local_transcriber.whisper.load_model")
def test_transcribe_success(mock_load_model, tmp_path):
    mock_model = mock_load_model.return_value
    mock_model.transcribe.return_value = {
        "text": "Hello world",
        "segments": [{"start": 0.0, "end": 1.0, "text": "Hello world"}],
        "language": "en",
    }

    audio_path = tmp_path / "test.wav"
    audio_path.write_text("fake audio")

    transcriber = LocalWhisperAdapter(model_size="tiny")
    result = transcriber.transcribe(audio_path)

    assert isinstance(result, TranscriptionResult)
    assert result.text == "Hello world"
    assert result.language == "en"
    assert len(result.segments) == 1

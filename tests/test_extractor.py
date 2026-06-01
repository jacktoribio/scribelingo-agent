from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

from src.adapters.video_extractor import VideoExtractorAdapter, AudioExtractionError


def test_extract_audio_file_not_found():
    extractor = VideoExtractorAdapter()
    with pytest.raises(FileNotFoundError):
        extractor.extract_audio(Path("nonexistent.mp4"))


@patch("src.adapters.video_extractor.VideoFileClip")
def test_extract_audio_no_audio_stream(mock_cls, tmp_path):
    mock_clip = mock_cls.return_value.__enter__.return_value
    mock_clip.audio = None

    video_path = tmp_path / "test.mp4"
    video_path.write_text("fake video")

    extractor = VideoExtractorAdapter()
    with pytest.raises(AudioExtractionError, match="No audio stream"):
        extractor.extract_audio(video_path)


@patch("src.adapters.video_extractor.VideoFileClip")
def test_extract_audio_success(mock_cls, tmp_path):
    mock_clip = mock_cls.return_value.__enter__.return_value
    mock_audio = MagicMock()
    mock_clip.audio = mock_audio

    video_path = tmp_path / "test.mp4"
    video_path.write_text("fake video")
    audio_path = tmp_path / "test.wav"

    extractor = VideoExtractorAdapter()
    result = extractor.extract_audio(video_path, audio_path)

    mock_audio.write_audiofile.assert_called_once()
    assert result == audio_path

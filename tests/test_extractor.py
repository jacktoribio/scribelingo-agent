from pathlib import Path
from unittest.mock import patch

import pytest

from src.video.extractor import VideoExtractor, AudioExtractionError


def test_extract_audio_file_not_found():
    extractor = VideoExtractor()
    with pytest.raises(FileNotFoundError):
        extractor.extract_audio(Path("nonexistent.mp4"))


@patch("src.video.extractor.VideoFileClip")
def test_extract_audio_no_audio_stream(mock_cls):
    mock_clip = mock_cls.return_value.__enter__.return_value
    mock_clip.audio = None

    extractor = VideoExtractor()
    with pytest.raises(AudioExtractionError, match="No audio stream"):
        extractor.extract_audio(Path("test.mp4"))


@patch("src.video.extractor.VideoFileClip")
def test_extract_audio_success(mock_cls, tmp_path):
    mock_clip = mock_cls.return_value.__enter__.return_value
    mock_clip.audio = True
    mock_audio = mock_clip.audio

    video_path = tmp_path / "test.mp4"
    video_path.write_text("fake video")
    audio_path = tmp_path / "test.wav"

    extractor = VideoExtractor()
    result = extractor.extract_audio(video_path, audio_path)

    mock_audio.write_audiofile.assert_called_once()
    assert result == audio_path

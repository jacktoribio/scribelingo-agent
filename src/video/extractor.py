from pathlib import Path
from typing import Optional

from moviepy import VideoFileClip


class AudioExtractionError(Exception):
    pass


class VideoExtractor:
    def __init__(self, ffmpeg_path: Optional[str] = None):
        self.ffmpeg_path = ffmpeg_path

    def extract_audio(
        self, video_path: Path, audio_path: Optional[Path] = None
    ) -> Path:
        video_path = Path(video_path).resolve()
        if not video_path.exists():
            raise FileNotFoundError(f"Video not found: {video_path}")

        if audio_path is None:
            audio_path = video_path.with_suffix(".wav")
        audio_path = Path(audio_path).resolve()

        try:
            with VideoFileClip(str(video_path)) as clip:
                if clip.audio is None:
                    raise AudioExtractionError(
                        f"No audio stream found in {video_path}"
                    )
                clip.audio.write_audiofile(
                    str(audio_path),
                    fps=16000,
                    nbytes=2,
                    codec="pcm_s16le",
                    ffmpeg_params=["-ac", "1"],
                    logger=None,
                )
        except AudioExtractionError:
            raise
        except Exception as exc:
            raise AudioExtractionError(
                f"Failed to extract audio from {video_path}: {exc}"
            ) from exc

        return audio_path

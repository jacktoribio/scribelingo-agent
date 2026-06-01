import argparse
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import nltk

from dotenv import load_dotenv

from src.adapters.html_reporter import ReportGenerator
from src.adapters.llm_analyzer import LLMAnalyzerAdapter
from src.core.models import TranscriptionResult
from src.adapters.local_transcriber import LocalWhisperAdapter
from src.adapters.openai_transcriber import OpenAIAPIAdapter
from src.adapters.video_extractor import (
    AudioExtractionError,
    VideoExtractorAdapter,
)

load_dotenv()

_NLTK_RESOURCES = ["punkt_tab", "punkt", "stopwords", "averaged_perceptron_tagger_eng"]


def _ensure_nltk_resources() -> None:
    for resource in _NLTK_RESOURCES:
        try:
            nltk.data.find(resource)
        except LookupError:
            nltk.download(resource, quiet=True)


BACKENDS = {
    "local": LocalWhisperAdapter,
    "openai": OpenAIAPIAdapter,
}


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="English Learning Agent — extract learning content "
        "from video conversations"
    )
    parser.add_argument(
        "--video",
        type=str,
        required=True,
        help="Path to video file (MP4, AVI, MOV, etc.)",
    )
    parser.add_argument(
        "--output",
        type=str,
        default=None,
        help="Output directory for the report (default: same as video)",
    )
    parser.add_argument(
        "--format",
        type=str,
        choices=["html", "md"],
        default="html",
        help="Report format (default: html)",
    )
    parser.add_argument(
        "--backend",
        type=str,
        choices=list(BACKENDS),
        default="local",
        help="Transcription backend: local (Whisper) or openai (API)",
    )
    parser.add_argument(
        "--model",
        type=str,
        default=None,
        help="Model override: Whisper model size (local) or API model name (openai). "
        "Defaults: base (local), whisper-1 (openai).",
    )
    return parser.parse_args(argv)


def _build_transcriber(args: argparse.Namespace):
    backend_cls = BACKENDS[args.backend]
    if args.backend == "local":
        return backend_cls(model_size=args.model or "base")
    return backend_cls(model=args.model or "whisper-1")


def _do_transcribe(transcriber, audio_path: Path, transcript_path: Path) -> TranscriptionResult:
    print(f"[2/5] Transcribing audio ({transcriber.__class__.__name__})...")
    try:
        transcript = transcriber.transcribe(audio_path)
    except Exception as exc:
        print(f"Transcription failed: {exc}", file=sys.stderr)
        sys.exit(1)

    if not transcript.text.strip():
        print("No speech detected in the audio.", file=sys.stderr)
        sys.exit(1)

    transcript_path.write_text(transcript.text, encoding="utf-8")
    print(f"       Transcript saved to: {transcript_path}")
    return transcript


def main(argv: list[str] | None = None) -> None:
    _ensure_nltk_resources()

    args = parse_args(argv)

    video_path = Path(args.video).resolve()
    
    if args.output:
        output_dir = Path(args.output).resolve()
        output_dir.mkdir(parents=True, exist_ok=True)
    else:
        output_dir = video_path.parent

    report_path = output_dir / f"{video_path.stem}_report.{args.format}"
    transcript_path = output_dir / f"{video_path.stem}_transcript.txt"
    audio_path = video_path.with_suffix(".wav")
    print(f"Output directory: {output_dir}")
    print(f"Output transcript_path: {transcript_path}")

    if transcript_path.exists():
        print("[1/5] Loading existing transcript...")
        with open(transcript_path, encoding="utf-8") as f:
            transcript = TranscriptionResult(
                text=f.read().strip(), segments=[], language=""
            )

    elif audio_path.exists():
        print("[1/5] Audio found, skipping extraction.")
        transcriber = _build_transcriber(args)
        transcript = _do_transcribe(transcriber, audio_path, transcript_path)

    else:
        print(f"Looking for video: {video_path}")

        print(f"[1/5] Extracting audio from {video_path.name}...")
        extractor = VideoExtractorAdapter()
        try:
            extractor.extract_audio(video_path, audio_path)
        except AudioExtractionError as exc:
            print(f"Audio extraction failed: {exc}", file=sys.stderr)
            sys.exit(1)

        if not audio_path.exists():
            print(f"Audio file not found after extraction: {audio_path}", file=sys.stderr)
            sys.exit(1)
        print(f"       Audio saved to: {audio_path}")

        transcriber = _build_transcriber(args)
        transcript = _do_transcribe(transcriber, audio_path, transcript_path)

    if not transcript.text.strip():
        print("No transcript text available.", file=sys.stderr)
        sys.exit(1)

    print("[3/5] Analyzing text with LLM...")
    analyzer = LLMAnalyzerAdapter()
    try:
        analysis = analyzer.analyze(transcript.text)
    except Exception as exc:
        print(f"Analysis failed: {exc}", file=sys.stderr)
        sys.exit(1)

    if not analysis.markdown.strip():
        print("Warning: analysis returned empty content.", file=sys.stderr)

    print(f"[4/5] Generating {args.format.upper()} report...")
    reporter = ReportGenerator()
    reporter.generate(
        transcript=transcript.text,
        analysis=analysis,
        output_path=report_path,
        format=args.format,
    )

    if not report_path.exists():
        print(f"Report file not found after generation: {report_path}", file=sys.stderr)
        sys.exit(1)

    print(f"[5/5] Done! Report saved to: {report_path}")


if __name__ == "__main__":
    main()

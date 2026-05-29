import argparse
import sys
from pathlib import Path

from src.video.extractor import VideoExtractor, AudioExtractionError
from src.transcription.transcriber import Transcriber, TranscriptionError
from src.analysis.phrases import PhraseAnalyzer
from src.analysis.grammar import GrammarAnalyzer
from src.analysis.vocabulary import VocabularyAnalyzer
from src.reporting.reporter import Reporter
from src.utils.helpers import validate_video_file


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
        "--model",
        type=str,
        choices=["tiny", "base", "small", "medium", "large"],
        default="base",
        help="Whisper model size (default: base)",
    )
    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> None:
    args = parse_args(argv)

    video_path = validate_video_file(Path(args.video))

    if args.output:
        output_dir = Path(args.output).resolve()
        output_dir.mkdir(parents=True, exist_ok=True)
    else:
        output_dir = video_path.parent

    report_path = output_dir / f"{video_path.stem}_report.{args.format}"

    print(f"[1/5] Extracting audio from {video_path.name}...")
    extractor = VideoExtractor()
    try:
        audio_path = video_path.with_suffix(".wav")
        extractor.extract_audio(video_path, audio_path)
    except AudioExtractionError as exc:
        print(f"Audio extraction failed: {exc}", file=sys.stderr)
        sys.exit(1)

    print("[2/5] Transcribing audio with Whisper...")
    transcriber = Transcriber(model_size=args.model)
    try:
        transcript = transcriber.transcribe(audio_path)
    except TranscriptionError as exc:
        print(f"Transcription failed: {exc}", file=sys.stderr)
        sys.exit(1)

    if not transcript.text.strip():
        print("No speech detected in the audio.", file=sys.stderr)
        sys.exit(1)

    print("[3/5] Analyzing phrases, grammar, and vocabulary...")
    phrase_analyzer = PhraseAnalyzer()
    grammar_analyzer = GrammarAnalyzer()
    vocab_analyzer = VocabularyAnalyzer()

    phrases = phrase_analyzer.extract(transcript.text)
    grammar = grammar_analyzer.extract(transcript.text)
    vocabulary = vocab_analyzer.extract(transcript.text)

    print(f"[4/5] Generating {args.format.upper()} report...")
    reporter = Reporter()
    reporter.generate(
        transcript=transcript.text,
        phrases=phrases,
        grammar=grammar,
        vocabulary=vocabulary,
        output_path=report_path,
        format=args.format,
    )

    print(f"[5/5] Done! Report saved to: {report_path}")


if __name__ == "__main__":
    main()

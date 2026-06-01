# AGENTS.md — Project-Level Instructions for AI Assistants

## Project
**ScribeLingo Agent** — Autonomous pipeline that transforms video/audio content into structured linguistic study guides for advanced language learning.

## Tech Stack
- Python 3.11+
- Hexagonal Architecture (Ports & Adapters)
- `openai-whisper` for local speech-to-text
- `openai` for cloud speech-to-text (Whisper API)
- `spaCy` for NLP (POS tagging, dependency parsing)
- `nltk` / `scikit-learn` for n-gram & frequency analysis
- `ffmpeg` / `moviepy` for audio extraction from video

## Conventions
- Use type hints for all function signatures
- Follow PEP 8 (line length 100)
- Write docstrings for all public modules, classes, and functions (Google style)
- Use `pathlib.Path` for file paths
- Keep functions small and single-purpose
- Domain logic goes in `src/core/`, infrastructure in `src/adapters/`

## Security
- NEVER read, display, output, or reference the contents of `.env` files.
- When asked about configuration, refer to `.env.example` instead.

## Commands
```powershell
# Install dependencies
pip install -e .

# Download spaCy model
python -m spacy download en_core_web_sm

# Run with local Whisper (default)
python src/main.py --video samples/example.mp4

# Run with OpenAI API
python src/main.py --video samples/example.mp4 --backend openai

# Run tests
python -m pytest tests/ -v

# Type check
python -m mypy src/
```

## Project Structure
```
ingles-ayuda/
├── AGENTS.md
├── docs/SDD.md
├── docs/TODO.md
├── src/
│   ├── main.py              # Composition root
│   ├── core/                # Domain logic (no external deps)
│   │   ├── ports.py         # Abstract interfaces
│   │   ├── models.py        # Shared domain models
│   │   ├── phrases.py       # N-gram / collocation analysis
│   │   ├── grammar.py       # POS & dependency pattern mining
│   │   └── vocabulary.py    # Frequency & TF-IDF analysis
│   ├── adapters/            # Infrastructure implementations
│   │   ├── video_extractor.py
│   │   ├── local_transcriber.py
│   │   ├── openai_transcriber.py
│   │   └── html_reporter.py
│   └── utils/
│       └── helpers.py
├── tests/
├── samples/
└── requirements.txt
```

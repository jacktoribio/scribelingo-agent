# Software Design Document — ScribeLingo Agent

## 1. Introduction

### 1.1 Purpose
This document describes the architecture, component design, and implementation plan for **ScribeLingo Agent** — an autonomous pipeline that transforms video/audio content into structured linguistic study guides for advanced language learning.

### 1.2 Scope
The system accepts video files (MP4, AVI, MOV), extracts audio, transcribes speech to text (via local Whisper or OpenAI API), analyzes the transcript for learning content, and produces a structured report.

### 1.3 Definitions
| Term | Definition |
|------|-----------|
| **STT** | Speech-to-Text, conversion of audio to text |
| **N-gram** | Contiguous sequence of N items from text |
| **Collocation** | Sequence of words that co-occur more often than chance |
| **POS** | Part of Speech (noun, verb, adjective, etc.) |
| **TF-IDF** | Term Frequency–Inverse Document Frequency |
| **PMI** | Pointwise Mutual Information for collocation scoring |
| **Port** | Interface/abstract class defining a boundary between core and infrastructure |
| **Adapter** | Concrete implementation of a port |

---

## 2. Architecture: Hexagonal (Ports & Adapters)

### 2.1 Design Principle
The system follows **Hexagonal Architecture** (also called Ports & Adapters) to isolate the core domain logic from external infrastructure concerns. This makes the system testable, maintainable, and allows swapping implementations without touching business logic.

### 2.2 High-Level Diagram

```
                          ┌──────────────────────────┐
                          │      CLI (main.py)        │
                          │     Composition Root      │
                          └──────┬─────────┬─────────┘
                                 │         │
                    ┌────────────┼─────────┼────────────────────┐
                    │            │         │                    │
                    │    ┌───────▼─────────▼──────┐             │
                    │    │      Ports (ABCs)       │             │
                    │    │  ┌──────────────────┐  │             │
                    │    │  │ AudioExtractor    │  │             │
                    │    │  │ Transcriber       │  │             │
                    │    │  │ ReportGenerator   │  │             │
                    │    │  └──────────────────┘  │             │
                    │    └───────┬─────────▲──────┘             │
                    │            │         │                    │
                    │    ┌───────┼─────────┼──────────┐         │
                    │    │       │         │          │         │
                    │    ▼       ▼         │          │         │
                    │  ┌─────┐ ┌──────┐   │          │         │
                    │  │Video│ │Local │   │          │         │
                    │  │Ext. │ │Whisp.│   │          │         │
                    │  │Adap.│ │Adap. │   │          │         │
                    │  └─────┘ └──────┘   │          │         │
                    │           ┌─────────┴──────┐   │         │
                    │           │  OpenAI API     │   │         │
                    │           │  Adapter        │   │         │
                    │           └────────────────┘   │         │
                    │                      ┌─────────┴──────┐  │
                    │                      │  HTML Reporter │  │
                    │                      │  Adapter       │  │
                    │                      └────────────────┘  │
                    │         Adapters Layer                    │
                    └──────────────────────────────────────────┘

                    ┌──────────────────────────────────────────┐
                    │           Domain Core                     │
                    │  ┌────────────┐ ┌──────────┐ ┌─────────┐ │
                    │  │ Phrase     │ │ Grammar  │ │Vocab    │ │
                    │  │ Analyzer   │ │ Analyzer │ │Analyzer │ │
                    │  └────────────┘ └──────────┘ └─────────┘ │
                    └──────────────────────────────────────────┘
```

### 2.3 Ports (Interfaces)

Defined in `src/core/ports.py`:

| Port | Method | Purpose |
|------|--------|---------|
| `AudioExtractorPort` | `extract_audio(video_path, audio_path) -> Path` | Extract audio from video |
| `TranscriberPort` | `transcribe(audio_path) -> TranscriptionResult` | Convert audio to text |
| `ReportGeneratorPort` | `generate(transcript, phrases, grammar, vocab, output_path, format) -> Path` | Produce learning report |

### 2.4 Adapters (Implementations)

| Adapter | Implements | Technology |
|---------|-----------|------------|
| `VideoExtractorAdapter` | `AudioExtractorPort` | moviepy / ffmpeg |
| `LocalWhisperAdapter` | `TranscriberPort` | openai-whisper (local model) |
| `OpenAIAPIAdapter` | `TranscriberPort` | OpenAI Whisper API |
| `HTMLReporterAdapter` | `ReportGeneratorPort` | jinja2 / string formatting |

### 2.5 Domain Core

Located in `src/core/`. Contains only pure business logic with no external dependencies:

| Module | Class | Responsibility |
|--------|-------|---------------|
| `phrases.py` | `PhraseAnalyzer` | N-gram counting, collocation scoring (PMI) |
| `grammar.py` | `GrammarAnalyzer` | POS tag pattern mining, dependency triple extraction |
| `vocabulary.py` | `VocabularyAnalyzer` | Word frequency, lemmatization, TF-IDF keyword extraction |
| `models.py` | Shared dataclasses | `TranscriptionResult`, `PhrasesResult`, `GrammarResult`, `VocabularyResult` |

### 2.6 Composition Root (`src/main.py`)

`main.py` acts as the **composition root** — it instantiates concrete adapters and wires them together. Users select the transcription backend via `--backend`:
- `--backend local` → `LocalWhisperAdapter` (default)
- `--backend openai` → `OpenAIAPIAdapter`

---

## 3. Data Flow

1. **Input**: Video file path → `VideoExtractorAdapter.extract_audio()` → temporary WAV file
2. **Transcription**: Audio file → `TranscriberPort.transcribe()` (local Whisper or OpenAI API) → `TranscriptionResult`
3. **Analysis** (no external deps):
   - Text → `PhraseAnalyzer.extract()` → ranked n-grams & collocations
   - Text → `GrammarAnalyzer.extract()` → frequent POS patterns & dependency triples
   - Text → `VocabularyAnalyzer.extract()` → word frequency list, TF-IDF scores
4. **Output**: Analysis results → `HTMLReporterAdapter.generate()` → HTML/MD report file

---

## 4. Component Specifications

### 4.1 AudioExtractorPort → VideoExtractorAdapter

```python
class VideoExtractorAdapter(AudioExtractorPort):
    def __init__(self, ffmpeg_path: str | None = None)
    def extract_audio(self, video_path: Path, audio_path: Path | None = None) -> Path
```

**Input**: Video file (MP4, AVI, MOV, MKV)
**Output**: 16kHz mono WAV file
**Dependencies**: `moviepy`
**Error handling**: Raises `AudioExtractionError`

### 4.2 TranscriberPort → LocalWhisperAdapter

```python
class LocalWhisperAdapter(TranscriberPort):
    def __init__(self, model_size: str = "base")
    def transcribe(self, audio_path: Path) -> TranscriptionResult
```

**Dependencies**: `openai-whisper` (local model download)
**Model sizes**: tiny (~1GB), base (~1.5GB), small (~3GB), medium (~6GB), large (~12GB)

### 4.3 TranscriberPort → OpenAIAPIAdapter

```python
class OpenAIAPIAdapter(TranscriberPort):
    def __init__(self, api_key: str | None = None, model: str = "whisper-1")
    def transcribe(self, audio_path: Path) -> TranscriptionResult
```

**Dependencies**: `openai` Python package, valid `OPENAI_API_KEY` env var
**Notes**: Reads API key from `OPENAI_API_KEY` environment variable or constructor argument

### 4.4 PhraseAnalyzer

```python
class PhraseAnalyzer:
    def extract(self, text: str, ngram_range: tuple = (2, 5), top_n: int = 50) -> PhrasesResult
```

**Algorithm**: Tokenize → filter stopwords → count n-gram frequencies → score collocations via PMI

### 4.5 GrammarAnalyzer

```python
class GrammarAnalyzer:
    def extract(self, text: str, top_n: int = 30) -> GrammarResult
```

**Algorithm**: spaCy parse → extract POS tag sequences → extract dependency triples → count & rank

### 4.6 VocabularyAnalyzer

```python
class VocabularyAnalyzer:
    def extract(self, text: str, top_n: int = 50) -> VocabularyResult
```

**Algorithm**: spaCy tokenize → lemmatize → count word/lemma frequencies → compute TF-IDF

### 4.7 ReportGeneratorPort → HTMLReporterAdapter

```python
class HTMLReporterAdapter(ReportGeneratorPort):
    def generate(self, transcript: str, phrases: PhrasesResult,
                 grammar: GrammarResult, vocabulary: VocabularyResult,
                 output_path: Path, format: str = "html") -> Path
```

**Output formats**: HTML (styled table layout) or Markdown (GitHub-flavored tables)

---

## 5. Data Dictionary

| Component | Input | Output |
|-----------|-------|--------|
| VideoExtractorAdapter | Video file (.mp4, .avi, .mov) | Audio file (.wav, 16kHz mono) |
| LocalWhisperAdapter / OpenAIAPIAdapter | Audio file (.wav) | `TranscriptionResult` |
| PhraseAnalyzer | Plain text | `PhrasesResult` |
| GrammarAnalyzer | Plain text | `GrammarResult` |
| VocabularyAnalyzer | Plain text | `VocabularyResult` |
| HTMLReporterAdapter | All results + transcript | Report file (.html/.md) |

---

## 6. Interface Design

### 6.1 CLI Interface
```
python src/main.py --video <path>
                   [--output <dir>]
                   [--format html|md]
                   [--backend local|openai]
                   [--model <model_name>]
```

### 6.2 Environment Variables
| Variable | Required For | Description |
|----------|-------------|-------------|
| `OPENAI_API_KEY` | `--backend openai` | OpenAI API key for cloud transcription |

### 6.3 Streamlit Interface (Future)
- File upload widget
- Backend selector dropdown
- Real-time processing status
- Interactive report viewing

---

## 7. Error Handling

| Error | Cause | Handling |
|-------|-------|----------|
| `FileNotFoundError` | Video file missing | Check path, raise descriptive error |
| `AudioExtractionError` | FFmpeg/moviepy failure | Log ffmpeg stderr, raise |
| `TranscriptionError` | Whisper/API failure | Validate audio, raise with API error details |
| `EmptyTranscriptError` | No speech detected | Check audio duration, raise warning |
| `MissingAPIKeyError` | OpenAI key not set | Guide user to set `OPENAI_API_KEY` |

---

## 8. Testing Strategy

- **Unit tests** for each analyzer with known text inputs and expected outputs
- **Adapter tests** with mocked external dependencies (moviepy, whisper, openai)
- **Integration test** with a small sample video (~30s)
- Use `pytest` with `pytest-cov` for coverage

---

## 9. Project Structure

```
ingles-ayuda/
├── src/
│   ├── main.py                    # Composition root (CLI entry point)
│   ├── core/                      # Domain — no external deps
│   │   ├── ports.py               # Abstract interfaces
│   │   ├── models.py              # Shared domain models
│   │   ├── phrases.py             # N-gram & collocation analysis
│   │   ├── grammar.py             # POS & dependency pattern mining
│   │   └── vocabulary.py          # Frequency & TF-IDF analysis
│   ├── adapters/                  # Infrastructure implementations
│   │   ├── video_extractor.py     # Audio extraction via moviepy
│   │   ├── local_transcriber.py   # Whisper local transcription
│   │   ├── openai_transcriber.py  # OpenAI API transcription
│   │   └── html_reporter.py       # HTML/Markdown report generation
│   └── utils/
│       └── helpers.py             # File validation, text cleaning
├── tests/
├── docs/SDD.md
├── .env.example
└── requirements.txt
```

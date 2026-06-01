# ScribeLingo Agent 🤖📚

[![Python Version](https://img.shields.io/badge/python-3.11+-blue.svg)](https://www.python.org)
[![OpenAI Models](https://img.shields.io/badge/LLM-GPT--5%20%7C%20o3%2Fo4-orange.svg)](https://openai.com)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

**ScribeLingo Agent** is an autonomous pipeline that transforms raw video/audio content into structured, pedagogical study guides. Instead of generic grammar definitions, it maps linguistic patterns directly to the speaker's own words, ranked by frequency — so you know what to study first.

---

## 🚀 Key Features

- **Automated Media Pipeline** — Extracts audio from video, transcribes with Whisper (local or OpenAI API), and saves checkpoints so you never re-process work.
- **LLM-Powered Linguistic Analysis** — Uses GPT-5 / o-series to analyze transcripts for verb tenses, idioms, phrasal verbs, key vocabulary, and sentence patterns — all sorted by frequency of appearance.
- **Frequency-Driven Sorting** — Every section prioritizes patterns from most to least frequent, so you study what the speaker actually used most.
- **Structured Study Guide Output** — Generates clean HTML or Markdown reports with 5 pedagogical sections plus a quick-study challenge.
- **Checkpoint Resume** — Already have a transcript or audio file? The pipeline picks up from where you left off (transcript → audio → video).

---

## 🛠️ Architecture & Workflow

```
┌──────────────────────────────────────────────────┐
│              ScribeLingo Pipeline                │
├──────────────────────────────────────────────────┤
│                                                  │
│  ┌──────────────┐   missing    ┌──────────────┐  │
│  │ transcript   │─────────────→│   audio .wav  │  │
│  │    .txt      │              │              │  │
│  └──────┬───────┘              └──────┬───────┘  │
│         │ exists                     │ exists    │
│         ▼                            ▼           │
│  ┌──────────────┐           ┌──────────────┐     │
│  │  Load text   │           │  Transcribe  │     │
│  └──────┬───────┘           └──────┬───────┘     │
│         │                          │              │
│         └──────────┬───────────────┘              │
│                    ▼                              │
│         ┌──────────────────┐                      │
│         │  missing audio   │  ┌──────────────┐    │
│         │  & transcript    │──│ video .mp4    │    │
│         │                  │  │ extract audio │    │
│         └──────────────────┘  └──────┬───────┘    │
│                    │                 │             │
│                    ▼                 ▼             │
│         ┌──────────────────────────────────┐      │
│         │         LLM Analysis             │      │
│         │   (GPT-5 / o-series)             │      │
│         └──────────────┬───────────────────┘      │
│                        ▼                          │
│         ┌──────────────────────────────────┐      │
│         │     Report Generation            │      │
│         │   (HTML or Markdown)             │      │
│         └──────────────────────────────────┘      │
│                                                  │
└──────────────────────────────────────────────────┘
```

### Component Overview

| Component | Description |
|-----------|-------------|
| `src/main.py` | Composition root — orchestrates the 3-branch checkpoint pipeline |
| `src/adapters/video_extractor.py` | Extracts audio track from video via `moviepy` |
| `src/adapters/local_transcriber.py` | Local transcription using `openai-whisper` |
| `src/adapters/openai_transcriber.py` | Cloud transcription via OpenAI Whisper API |
| `src/adapters/llm_analyzer.py` | Sends transcript to GPT-5 / o-series with a structured prompt |
| `src/adapters/html_reporter.py` | Converts LLM analysis to HTML or Markdown study guide |
| `src/core/ports.py` | Abstract interfaces (Ports & Adapters pattern) |
| `src/core/models.py` | Shared dataclasses (`TranscriptionResult`, `LLMAnalysisResult`) |

---

## ⚙️ Configuration

### Environment Variables (`.env`)

| Variable | Required | Default | Description |
|----------|----------|---------|-------------|
| `OPENAI_API_KEY` | Yes (for `--backend openai` and LLM analysis) | — | Your OpenAI API key |

### CLI Arguments

```
usage: python src/main.py --video <path> [options]

Required:
  --video PATH              Path to video file (MP4, AVI, MOV, etc.)

Options:
  --output DIR              Output directory (default: same as video)
  --format {html,md}        Report format (default: html)
  --backend {local,openai}  Transcription backend (default: local)
  --model MODEL             Model override:
                              local  → whisper model size (default: base)
                              openai → API model name (default: whisper-1)
                              LLM    → model for analysis (default: gpt-5.4-mini)
```

---

## 📦 Example Output

Below is a real excerpt from a generated Markdown study guide (using `--format md`):

```markdown
# English Learning Report

## Transcript

I think we should pause and consider the implications. This is not only a technical challenge but also a cultural shift.

---

### 1. Common Verb Tenses & Grammatical Structures

* **Modal Verbs (should + base verb)**: Used to give recommendations or express obligation.
  - "I think we **should pause** and consider the implications."
  - "We **should consider** the long-term effects."

* **Present Simple**: Used for stating facts or opinions.
  - "I **think** we should pause."
  - "This **is** not only a technical challenge."

### 2. Idiomatic Expressions & Phrasal Verbs

* **"Pause and consider"**: A natural collocation meaning to stop and think carefully before acting.
  - "I think we should **pause and consider** the implications."

### 3. Advanced or Key Vocabulary

* **Implications**: Definition: possible effects or results of an action | Synonym: consequences, repercussions
  - "Consider the **implications**."

### 4. Sentence Patterns for Practice

* Pattern 1: "I think we should pause and consider the implications."
  * Template to mimic: **"I think we should [verb] and [verb] the [noun]."**
* Pattern 2: "This is not only a technical challenge but also a cultural shift."
  * Template to mimic: **"This is not only [X] but also [Y]."**
```

---

## 🚀 Quick Start

### Local Setup

```powershell
python -m venv .venv
.venv\Scripts\activate
pip install -e .
python -m spacy download en_core_web_sm

# Run with local Whisper (requires ffmpeg on PATH)
python src/main.py --video samples\example.mp4

# Run with OpenAI API
python src/main.py --video samples\example.mp4 --backend openai
```

### Docker

```powershell
docker build -t scribelingo .
docker run --rm -v "$(pwd)/samples:/app/samples" scribelingo --video samples/example.mp4
```

---

## 📁 Project Structure

```
ScribeLingo/
├── AGENTS.md                 # AI assistant instructions
├── docs/
│   ├── SDD.md                # Software Design Document
│   └── TODO.md               # Roadmap
├── src/
│   ├── main.py               # Composition root & pipeline orchestration
│   ├── core/                 # Domain logic (no external deps)
│   │   ├── ports.py          # Abstract interfaces
│   │   ├── models.py         # Shared dataclasses
│   │   └── ...               # Legacy analyzers (replaced by LLM)
│   ├── adapters/             # Infrastructure implementations
│   │   ├── video_extractor.py
│   │   ├── local_transcriber.py
│   │   ├── openai_transcriber.py
│   │   ├── llm_analyzer.py   # GPT-powered linguistic analysis
│   │   └── html_reporter.py  # Report renderer (HTML / Markdown)
│   └── utils/
│       └── helpers.py
├── tests/                    # Pytest test suite
├── samples/                  # Sample video files
├── .env.example
├── requirements.txt
└── pyproject.toml
```

---

## 🧪 Running Tests

```powershell
.venv\Scripts\activate
python -m pytest tests/ -v
```

---

## 📄 License

MIT

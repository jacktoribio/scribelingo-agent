# TODO — ScribeLingo Agent

## Phase 1: Project Scaffold
- [x] Create folder structure
- [x] Create `AGENTS.md`
- [x] Create `docs/SDD.md`
- [x] Create `docs/TODO.md`
- [x] Create `requirements.txt`
- [x] Create `README.md`
- [x] Create `src/__init__.py` and sub-package `__init__.py` files
- [x] Create `.gitignore`
- [x] Create `scripts/setup.ps1` — automated venv setup
- [x] Create `Makefile` — dev/test/build targets
- [x] Create `Dockerfile`
- [x] Create `.dockerignore`
- [x] Create `docker-compose.yml`
- [x] Create `pyproject.toml`
- [x] Fix `ModuleNotFoundError` — add `sys.path` + `pip install -e .`

## Phase 2: Hexagonal Architecture Refactor
- [x] Create `src/core/ports.py` — port interfaces (ABCs)
- [x] Create `src/core/models.py` — shared domain dataclasses
- [x] Create `src/adapters/video_extractor.py` — implements AudioExtractorPort
- [x] Create `src/adapters/local_transcriber.py` — implements TranscriberPort (Whisper)
- [x] Create `src/adapters/openai_transcriber.py` — implements TranscriberPort (API)
- [x] Create `src/adapters/html_reporter.py` — implements ReportGeneratorPort
- [x] Move analyzers to `src/core/` (phrases, grammar, vocabulary)
- [x] Remove old `src/analysis/`, `src/video/`, `src/transcription/`, `src/reporting/`
- [x] Update tests for new import paths
- [x] Update `docs/SDD.md` with hexagonial architecture & diagrams
- [x] Update `AGENTS.md` with .env security rule + new structure
- [x] Create `.env.example`
- [x] Update `requirements.txt` and `pyproject.toml` (openai, python-dotenv)

## Phase 3: Utilities
- [x] Implement `src/utils/helpers.py` (file validation, text cleaning, stopwords)

## Phase 4: Testing
- [ ] Install dependencies & run `pytest` to verify tests pass
- [ ] Integration test with sample video
- [ ] Write test for `src/adapters/openai_transcriber.py`

## Phase 5: Sample & Demo
- [ ] Add sample video/audio file
- [ ] Verify end-to-end pipeline works

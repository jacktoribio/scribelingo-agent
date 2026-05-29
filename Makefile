.PHONY: venv install test typecheck run docker-build docker-run clean

# ── Local Development ──────────────────────────────────────────

venv:
	python -m venv .venv
	.venv\Scripts\pip install --upgrade pip

install: venv
	.venv\Scripts\pip install -r requirements.txt
	.venv\Scripts\python -m spacy download en_core_web_sm

test:
	python -m pytest tests\ -v

typecheck:
	python -m mypy src\

run:
	python src\main.py --video samples\example.mp4 --output samples --format html

clean:
	rmdir /s /q .venv 2>nul || echo No .venv found
	del /q samples\*.wav 2>nul || echo No WAV files
	del /q samples\*.html 2>nul || echo No HTML reports

# ── Docker ─────────────────────────────────────────────────────

docker-build:
	docker build -t ingles-ayuda .

docker-run:
	docker run --rm -v "$(shell pwd)/samples:/app/samples" ingles-ayuda --video samples/example.mp4

docker-run-tests:
	docker run --rm ingles-ayuda python -m pytest tests\ -v

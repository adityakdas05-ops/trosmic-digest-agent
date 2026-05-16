# Trosmic Digest Agent

Trosmic Digest Agent is a local-first Python agent that gathers updates from RSS feeds and manual URLs, removes duplicates, scores items against your interests, and writes a Markdown plus JSON digest. The core package uses only the Python standard library so it can run in constrained environments. Optional Band/OpenAI dependencies are loaded only when you run the remote-agent entry point.

## What It Does

- Loads local settings from `.env` and `agent_config.yaml`.
- Fetches RSS feeds and manually listed web pages.
- Normalizes articles into a small internal model.
- Removes exact and near-duplicate stories.
- Scores items by source quality, interest matches, and recency.
- Produces a daily Markdown digest and a companion JSON artifact.
- Provides an optional Band runtime entry point for hosted/remote operation.

## Local Setup

```bash
uv sync
cp .env.example .env
cp agent_config.example.yaml agent_config.yaml
```

Edit `agent_config.yaml` with your sources and interests. Do not put API keys in it unless you keep it local; the real file is intentionally ignored by Git.

## Run Tests

```bash
PYTHONPATH=src uv run python -m unittest discover -s tests
PYTHONPATH=src uv run python -m compileall src tests
ruff check .
```

On Windows PowerShell, use:

```powershell
$env:PYTHONPATH='src'
uv run python -m unittest discover -s tests
uv run python -m compileall src tests
ruff check .
```

## Generate A Digest

```bash
PYTHONPATH=src uv run python -m trosmic_digest_agent.main
```

Useful flags:

```bash
PYTHONPATH=src uv run python -m trosmic_digest_agent.main --config agent_config.yaml --date 2026-05-16 --print
PYTHONPATH=src uv run python -m trosmic_digest_agent.main --output-dir digests
```

## Scheduler

The scheduler is intentionally simple and local. It runs the digest once per day at a configured local time.

```bash
PYTHONPATH=src uv run python -m trosmic_digest_agent.scheduler --time 08:00
```

## Optional Band Runtime

Install optional remote-agent dependencies only when you need the Band runtime:

```bash
uv pip install thenvoi langchain-openai langgraph openai pyyaml
PYTHONPATH=src uv run python -m trosmic_digest_agent.band_app
```

Required secrets belong in your local `.env`, not in Git:

```bash
OPENAI_API_KEY=
BAND_API_KEY=
BAND_AGENT_ID=
```

## Repository Safety

The following files are ignored and should stay local:

- `.env`
- `agent_config.yaml`
- generated files under `digests/`

Commit the example files instead:

- `.env.example`
- `agent_config.example.yaml`

# Trosmic Digest Agent

Trosmic Digest Agent is a sports-business-first intelligence agent for Trosmic. It gathers updates from configured sports-business search groups, RSS feeds, and manual URLs, removes duplicates, applies a Trosmic Relevance Gate, and writes a Markdown plus JSON digest focused on sports media rights, OTT distribution, sponsorship, venues, franchise economics, league governance, fan data, combat sports, kabaddi, India/GCC sports capital, and Rumil-relevant intelligence.

It is not an AI-news-first digest. Generic AI startup, product, funding, crypto, or politics stories are excluded unless they directly affect sports, media, entertainment, venues, fan engagement, content production, athlete data, league operations, sponsorship analytics, or Trosmic's Rumil/D2F strategy.

## What It Does

- Loads local settings from `.env` and `agent_config.yaml`.
- Fetches the sports-business source catalog in `config/sources.yaml`, plus any local RSS feeds and manually listed web pages.
- Normalizes articles into a small internal model.
- Removes exact and near-duplicate stories.
- Scores every item using the 21-point Trosmic Relevance Gate.
- Produces a structured sports-business intelligence digest and companion JSON artifact.
- Provides an optional Band runtime entry point for hosted/remote operation.

## Trosmic Relevance Gate

Every item must score at least 14 out of 21 before it enters the digest:

- Direct relevance to a Trosmic pillar: 0-5
- Commercial materiality: 0-5
- Strategic insight value: 0-5
- Actionability for Trosmic: 0-3
- Source credibility: 0-3

Additional hard rules:

- Generic AI, generic tech, generic startup, SaaS, cloud, chips, crypto, and Web3 stories are rejected unless they have a direct sports/media/entertainment/venue/fan-data link.
- No sports/media/entertainment/venue/capital link means automatic rejection.
- No clear Trosmic implication means automatic rejection.
- At most one AI-led item can enter the Top 10, and only when it directly affects sports broadcast production, fan analytics, venue operations, sponsorship analytics, athlete data, or media rights.

Source priority:

- Tier 1: official league, company, government, and filing sources
- Tier 2: Reuters, Bloomberg, FT, CNBC, SBJ, SportBusiness, SportsPro, ESPN, Variety, Deadline, Economic Times, Mint, Business Standard, Sportstar
- Tier 3: KPMG, Deloitte, PwC, EY-FICCI, GroupM/WPP, Nielsen, BARC, Kearney, Houlihan Lokey
- Tier 4: LinkedIn, social, and weak signals, clearly labelled

The rendered digest sections are Executive Signal of the Day, Top 10 Trosmic-Relevant Developments, Opportunity Radar, Risk/Weak Signal Watchlist, Data Points to Save, and a 700-1,000 word Strategic Op-Ed.

Each run also prints and saves debug diagnostics to `digests/debug-YYYY-MM-DD.json`: total stories fetched, top fetched domains, per-story source domain/query metadata, generic AI rejections, generic tech rejections, no-pillar rejections, eligibility-pass count, final selected titles, selected relevance scores and pillars, and the number of AI-led items selected.

## Local Setup

```bash
uv sync
cp .env.example .env
cp agent_config.example.yaml agent_config.yaml
```

Edit `agent_config.yaml` with your sources and interests. Do not put API keys in it unless you keep it local; the real file is intentionally ignored by Git.

## Run Tests

```bash
uv run python -m pytest
uv run python -m unittest discover -s tests
uv run python -m compileall src tests
ruff check .
```

On Windows PowerShell, use:

```powershell
uv run python -m pytest
uv run python -m unittest discover -s tests
uv run python -m compileall src tests
ruff check .
```

## Generate A Digest

```bash
uv run python -m trosmic_digest_agent.main
```

Useful flags:

```bash
uv run python -m trosmic_digest_agent.main --config agent_config.yaml --date 2026-05-16 --print
uv run python -m trosmic_digest_agent.main --output-dir digests
```

## Scheduler

The scheduler is intentionally simple and local. It runs the digest once per day at a configured local time.

```bash
uv run python -m trosmic_digest_agent.scheduler --time 08:00
```

To run the daily job once immediately, use:

```bash
uv run python -m trosmic_digest_agent.scheduler.run_daily
```

To keep it running on a daily loop, use:

```bash
uv run python -m trosmic_digest_agent.scheduler.run_daily --loop --time 08:00
```

## Optional Band Runtime

Install optional remote-agent dependencies only when you need the Band runtime:

```bash
uv pip install "thenvoi-sdk[langgraph]" openai pyyaml
uv run python -m trosmic_digest_agent.band_app
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

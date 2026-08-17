# Marshal 🤖

> **Autonomous GitHub triage agent for solo maintainers and small teams.**

Marshal watches your GitHub repositories so you don't have to. It triages incoming issues, reviews pull requests, reasons over maintainer expertise and workload to assign ownership, flags stale work, and surfaces everything through Discord — not another dashboard nobody checks.

---

## The Problem

Solo maintainers and small teams don't have a dedicated triage person. Issues pile up unlabeled, PRs wait days for a first look, and the cognitive overhead of *who should handle what* falls entirely on whoever has the time to look. Stateless per-PR bots can stamp a label, but they forget everything the moment the webhook fires. They can't tell you a PR has been sitting for two weeks, they can't learn from past decisions, and they can't reason about team workload.

Marshal can.

---

## What Marshal Does

| Capability | Description |
|---|---|
| **Issue Triage** | Classifies and labels new issues, detects duplicates, and routes them to the right person based on expertise and current workload |
| **PR Summarization** | Generates concise, human-readable summaries of pull requests so reviewers know what they're walking into |
| **Ownership Assignment** | Reasons over maintainer skill profiles and workload to decide who should own an issue or review |
| **Staleness Detection** | Flags issues and PRs that have gone quiet — something stateless per-PR bots fundamentally cannot do |
| **Persistent Memory** | Stores outcomes and preferences in Postgres/pgvector so its judgment improves over time |
| **Discord-Native UX** | Posts notifications and summaries to a Discord channel — where the team already lives |

---

## Architecture

```
GitHub Webhooks
      |
      v
 FastAPI Server  ------------------------------------------+
      |                                                    |
      v                                                    v
  Marshal Agent                                   Postgres + pgvector
 (Strands Agents SDK)                          (shared memory & embeddings)
      |
      +-- GitHub Connector  (reads issues, PRs, labels, comments)
      +-- Discord Connector (posts summaries, assignments, stale alerts)
```

**Stack:**

- **Agent runtime** — [Strands Agents SDK](https://github.com/strands-agents/sdk-python)
- **Webhook server** — [FastAPI](https://fastapi.tiangolo.com/)
- **Memory layer** — PostgreSQL + pgvector (similarity search over past decisions)
- **LLM backend** — AWS Bedrock (configurable via `llm_api_key` for other providers)
- **Notifications** — Discord Bot API
- **Runtime** — Python 3.14+, managed with [uv](https://github.com/astral-sh/uv)

---

## Project Structure

```
marshal/
+-- src/
    +-- agent/              # Strands agent definition and tools
    +-- connectors/
    |   +-- github/         # GitHub API client
    |   +-- discord/        # Discord bot client
    +-- lib/
    |   +-- config.py       # Settings (pydantic-settings, .env)
    +-- models/             # SQLAlchemy ORM models
    +-- routes/
    |   +-- github.py       # Webhook endpoint (/github/...)
    +-- services/           # Business logic layer
    +-- main.py             # FastAPI app entry point
+-- pyproject.toml
+-- uv.lock
```

---

## Getting Started

### Prerequisites

- Python 3.14+
- [uv](https://docs.astral.sh/uv/getting-started/installation/)
- PostgreSQL with the [pgvector](https://github.com/pgvector/pgvector) extension
- A GitHub App or Personal Access Token with repo permissions
- A Discord Bot token and a channel ID for notifications

### Installation

```bash
git clone https://github.com/m-taqii/marshal.git
cd marshal
uv sync
```

### Configuration

Copy the example env file and fill in your values:

```bash
cp .env.example .env
```

```env
# App
APP_ENV=development
LOG_LEVEL=INFO

# Database
DATABASE_URL=postgresql+asyncpg://user:password@localhost:5432/marshal

# AWS (for Bedrock LLM)
AWS_REGION=us-east-1
AWS_ACCESS_KEY_ID=
AWS_SECRET_ACCESS_KEY=

# Or use a direct LLM API key
LLM_API_KEY=

# GitHub
GITHUB_TOKEN=ghp_...
GITHUB_WEBHOOK_SECRET=your_webhook_secret

# Discord
DISCORD_BOT_TOKEN=
DISCORD_NOTIFY_CHANNEL_ID=
```

### Running Locally

```bash
uv run uvicorn src.main:app --reload
```

The webhook endpoint will be available at `http://localhost:8000/github`.

To expose it for GitHub to reach during development, forward webhooks using a tool like [smee.io](https://smee.io/):

```bash
smee -u https://smee.io/your-channel --target http://localhost:8000/github
```

### Health Check

```bash
curl http://localhost:8000/health
# {"status": "ok", "message": "System Running Perfectly"}
```

---

## Why Discord Instead of a Dashboard

Dashboards require a habit change. Discord is where most small teams already communicate. Marshal posts summaries and assignments directly into a channel, so triage becomes part of the existing conversation flow rather than a separate tool to remember to open.

---

## License

[Apache 2.0](LICENSE)

---
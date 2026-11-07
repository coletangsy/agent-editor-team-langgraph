# Repository Guidelines

## Purpose

This repository is a small Python application that collects AI and data-science news and produces a weekly digest through a LangGraph team of agents. Keep the workflow reviewable and keep secrets in the local environment.

## Development

- Use Python 3.12 or newer and the `uv` project environment described by `pyproject.toml`.
- Run `uv run main.py` for a local collection run. The command reads `feeds.txt`, calls the configured model provider, and writes generated material under `digests/`.
- Keep API keys and local runtime logs out of Git. Do not treat generated digests or logs as source code.
- Make focused changes to `main.py`, `ai_news_team.py`, and `util.py`; update tests when a test suite is added or behavior becomes non-trivial.

## Documentation

- [README](README.md) is the quick-start and usage entry point.
- [ARCHITECTURE.md](ARCHITECTURE.md) describes the collection and agent flow.
- [CHANGELOG.md](CHANGELOG.md) records user-visible or workflow-significant changes.
- Update `ARCHITECTURE.md` when the feed, agent, model, output, or trust boundary changes. Update `CHANGELOG.md` for delivered behavior or repository workflow changes.

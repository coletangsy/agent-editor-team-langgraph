# Agent Editor Team LangGraph Architecture

## Purpose and current boundary

The repository is a local batch workflow for turning configured AI-news feeds into a Markdown digest. `main.py` is the entry point; `ai_news_team.py` owns the LangGraph/agent collaboration; `util.py` contains shared helpers; and `feeds.txt` is the source list. The checked-in project metadata is in `pyproject.toml`.

The application is not a hosted service. It does not define a database, web API, scheduler, or remote publication step. A run may call external feed endpoints and a model provider, then writes generated digest files and logs locally. Credentials belong in `.env` or the process environment and are not part of the repository contract.

## Runtime flow

```text
feeds.txt
   ↓
main.py ── fetch and normalize feed entries ──→ agent team in ai_news_team.py
                                                   ↓
                                      model-backed editing and summarization
                                                   ↓
                                   Markdown digest under the local output area
```

The agent team is the editing boundary: it receives the collected article material and produces the digest. Feed retrieval and output persistence remain outside the agent graph so that input sources and generated artifacts can be inspected independently.

## Operational notes

- A normal run is `uv run main.py`; use a temporary or ignored output directory while experimenting.
- Feed availability, model credentials, provider behavior, and generated text are external or run-specific evidence. Do not describe a digest as complete when collection or model calls failed.
- The Python application has no committed automated test suite. Repository automation has 22 safety tests: run `node --test .github/tests/delete-merged-branch.node-test.mjs`. Add a focused application test when changing runtime behavior.

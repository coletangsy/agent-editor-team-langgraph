# Agent Editor Team LangGraph

A Python application for generating AI news digests using LangGraph & DeepSeek Model.

## Features

- Scrapes and processes AI news feeds
- Generates weekly digests
- Team-based agent architecture

## Installation

1. Clone this repository:
```bash
git clone https://github.com/your-username/agent-editor-team-langgraph.git
```

2. Install UV (if not already installed):
Please refer to the official documentation - https://docs.astral.sh/uv/getting-started/installation/

## Configuration

Create a `.env` file with your API keys and settings:
```
OPENAI_API_KEY=your-api-key
FEEDS_FILE=feeds.txt
```

## Usage
Run the main script:
```bash
uv run main.py
```

This will:
1. Fetch the latest AI news from the feeds listed in `feeds.txt`
2. Process and analyze articles using LangGraph's team of AI agents
3. Generate a weekly digest markdown file in the `digests/` directory
4. Output progress logs to both console and `log/` directory
5. Use DeepSeek Model for content analysis and summarization

## Project Structure

```
agent-editor-team-langgraph/
├── .env - Environment variables
├── ai_news_team.py - Main team implementation
├── digests/ - Generated digest markdown files
├── feeds.txt - News feed URLs
├── main.py - Entry point
├── util.py - Utility functions
```

## License

MIT License

## Maintainer Documentation

- [Repository guidance](AGENTS.md)
- [Architecture](ARCHITECTURE.md)
- [Changelog](CHANGELOG.md)

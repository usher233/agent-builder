---
name: web-search
description: Web search capability via Tavily API. Use when the agent needs to search the internet, look up current information, or fetch web page content.
metadata:
  author: agent-builder
  version: "1.0.0"
  requires:
    - tavily-python>=0.3.0
---

# Web Search Skill

Gives agents the ability to search the web and fetch page content via the Tavily search API.

## Tools

- **search_web(query, max_results=5)** — Search the web, returns titles, URLs, and snippets
- **fetch_page(url)** — Fetch and extract text content from a URL

## Configuration

```toml
[skills.web-search]
tavily_api_key = "${TAVILY_API_KEY}"
max_results = 5
```

## .env

```
TAVILY_API_KEY=tvly-...
```

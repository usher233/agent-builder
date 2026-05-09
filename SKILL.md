---
name: agent-builder
description: Build production-ready AI agents with LangGraph, configurable LLM backends, FastAPI web UI, Telegram integration, and Langfuse observability. Use this skill whenever the user wants to build, scaffold, or create an AI agent, agentic application, chatbot with tools, or automated workflow. Trigger on phrases like "build an agent", "create a bot", "scaffold an AI app", "make a trading/support/analysis agent", "I want to build something with LangGraph", or any request involving agent construction. Even if the user is unsure what to build, use this skill to guide them.
metadata:
  author: viktor
  version: "1.0.0"
---

# Agent Builder

Build production-ready AI agents in Python. Two modes: **scaffold** and **wizard**.

## Mode Detection

- **Scaffold mode**: User has a clear idea. "Build me a trading agent", "I want a customer support bot". Generate the project directly.
- **Wizard mode**: User is exploring. "Help me build an agent", "I'm not sure what to use". Walk through decisions one at a time.

If unsure which mode, ask the user one question: "Do you know what kind of agent you want, or should I walk you through the options?"

## Scaffold Mode

When the user has a clear agent idea, generate a complete project following this structure:

```
<agent-name>/
├── pyproject.toml           # uv-managed deps
├── config.toml              # LLM, Langfuse, Telegram, Data config
├── .env.example
├── skills/                  # Domain knowledge .md files the agent can reference
│   ├── domain-basics.md     # Market/domain mechanics
│   ├── strategies.md        # Analysis methodology
│   └── risk-management.md   # Safety rules and guardrails
├── src/
│   ├── __init__.py
│   ├── main.py              # Entry point: starts web + bot
│   ├── config.py            # config.toml parser
│   ├── agent/
│   │   ├── __init__.py
│   │   ├── graph.py         # LangGraph StateGraph
│   │   ├── nodes.py         # Agent nodes
│   │   └── state.py         # TypedDict state
│   ├── tools/
│   │   └── __init__.py      # Domain tools
│   ├── web/
│   │   ├── __init__.py
│   │   ├── app.py           # FastAPI + SSE streaming
│   │   └── templates/
│   │       └── index.html
│   └── bot/
│       ├── __init__.py
│       └── telegram.py      # python-telegram-bot handler
├── tests/
│   └── test_agent.py
└── Dockerfile
```

### Step 1: Understand Requirements

Ask these questions (concurrently if possible):

1. What does the agent do? (domain, tasks, tools needed)
2. What LLM provider? (deepseek, anthropic, openai — configurable in config.toml)
3. Does it need Telegram? (default: yes)
4. Does it need Web UI? (default: yes, FastAPI on :8080)
5. Does it need Langfuse observability? (default: yes)

Skip questions the user has already answered.

### Step 2: Generate Files

Use `assets/template/` as the starting point. Read each template file, then write it to the target project directory with placeholders replaced.

**Placeholder replacements:**
- `{{AGENT_NAME}}` → kebab-case agent name
- `{{AGENT_DESCRIPTION}}` → one-line description
- `{{LLM_PROVIDER}}` → deepseek / anthropic / openai
- `{{LLM_MODEL}}` → model name
- `{{HAS_TELEGRAM}}` → true/false
- `{{HAS_WEB}}` → true/false

### Step 3: Adapt Tools

Based on the agent's domain, generate appropriate tools in `src/tools/`. Read `references/tool-patterns.md` for patterns (API wrappers, MCP connectors, data fetchers).

### Step 4: Verify

After generating, run:
```bash
cd <agent-name>
uv sync
uv run python -c "from src.agent.graph import build_graph; print('Agent OK')"
```

## Wizard Mode

Walk through these decisions one at a time. Present options with short descriptions:

1. **Agent type**: chatbot | data analyst | workflow automator | custom
2. **LLM provider**: anthropic | openai | deepseek | other (OpenAI-compatible)
3. **Interfaces**: Telegram bot | Web UI | both | CLI only
4. **Observability**: Langfuse | none
5. **Persistence**: checkpointing (SqliteSaver) | none
6. **Tools needed**: web search | file system | API calls | database | custom

After each answer, briefly confirm and move to the next question. Once all questions are answered, generate the project using the scaffold flow.

## LLM Configuration

The project uses `config.toml` for all configuration. See `references/llm-config.md` for the full spec.

Core principle: a factory function in `src/config.py` reads `config.toml` and returns the right `BaseChatModel`. Switching providers is a one-line config change — no code changes needed.

```toml
[llm]
provider = "deepseek"        # deepseek | anthropic | openai | custom
api_key = "${LLM_API_KEY}"
model = "deepseek-v4-pro"
base_url = "https://api.deepseek.com/v1"
temperature = 0.7
max_tokens = 4096
```

## LangGraph Patterns

See `references/langgraph-patterns.md` for basic patterns. For advanced patterns, read `references/langgraph-patterns-deep.md`:
- State definition with TypedDict + Annotated reducers
- Node design (single responsibility per node, async for I/O, partial binding for LLM)
- Conditional edges for routing, error handling, and fallbacks
- SqliteSaver checkpointing for replay (async patterns, fork/update_state)
- Human-in-the-loop with `interrupt()` and `Command(resume=...)`
- Streaming via `astream_events()` with event type filtering
- Tool binding patterns with `bind_tools()` and tool execution loops

## Agent State

Every agent uses this base state (extend as needed):

```python
class AgentState(TypedDict):
    messages: Annotated[list[BaseMessage], operator.add]
    thread_id: str
    # Add domain-specific fields below
```

## Observability (Langfuse)

See `references/langfuse-setup.md` for full setup guide including:
- config.toml configuration (cloud and self-hosted)
- LangGraph CallbackHandler integration
- Streaming with callbacks
- Custom attributes and metadata propagation
- Trace scoring and evaluation
- Self-hosted Docker setup

Quick start:
```toml
[langfuse]
public_key = "${LANGFUSE_PUBLIC_KEY}"
secret_key = "${LANGFUSE_SECRET_KEY}"
host = "https://cloud.langfuse.com"
```

```python
from langfuse.langchain import CallbackHandler
handler = CallbackHandler()
result = await graph.ainvoke(state, config={"callbacks": [handler]})
```

## Telegram Integration

Uses `python-telegram-bot` with async handlers. The bot receives messages, forwards them to the LangGraph agent, and sends responses back. Each chat has its own `thread_id` for session isolation and replay.

## Web UI

FastAPI serves:
- `/` — Chat interface (SSE streaming)
- `/api/chat` — POST endpoint for messages
- `/api/threads/{thread_id}/replay` — Replay a past conversation

The frontend uses HTMX for interactivity without heavy JS frameworks. Apply the `frontend-design` skill later for distinctive visual design.

## Infrastructure (systemd + Docker Compose)

Every agent project includes an `infra/` directory with systemd service files and a setup script. See `references/infrastructure.md` for detailed patterns.

```
infra/
├── docker-compose.langfuse.yml  # Langfuse self-hosted (6 containers)
├── langfuse.service              # systemd user unit for Docker Compose
├── <agent-name>.service          # systemd user unit for the agent
└── setup.sh                      # One-shot: install deps, enable services
```

### When Generating an Agent

1. Generate `infra/docker-compose.langfuse.yml` with the Langfuse stack
2. Generate `infra/langfuse.service` (Type=oneshot, RemainAfterExit=yes)
3. Generate `infra/<agent-name>.service` (Type=simple, Restart=on-failure)
4. Generate `infra/setup.sh` that:
   - Installs docker-compose-plugin if missing
   - Creates `.env` from `.env.example` if not present
   - Installs systemd units to `~/.config/systemd/user/`
   - Enables and starts both services
5. Run `bash infra/setup.sh` after generating the project

### Key Systemd Details

- Use **user-level systemd** (`systemctl --user`): no root needed for Python services
- Langfuse service uses `Type=oneshot` with `RemainAfterExit=yes` (docker compose exits after starting containers)
- Agent service uses `Type=simple` with `Restart=on-failure` (auto-restart on crash)
- Agent `After=langfuse.service` to prevent race conditions
- `EnvironmentFile=.env` keeps secrets out of systemd unit files
- Run `sudo loginctl enable-linger $USER` on servers to keep services alive after SSH disconnect

### Langfuse: Cloud vs Self-Hosted

- **Cloud (free tier)**: Recommended for solo devs. No infra to manage. `host = "https://cloud.langfuse.com"`
- **Self-hosted**: 6 Docker containers (postgres, clickhouse, redis, minio, langfuse-web, langfuse-worker). Use when data residency matters or event volume exceeds free tier. `host = "http://localhost:3000"`

## Domain Skills (skills/ folder)

Every agent should include a `skills/` directory with 2-3 markdown files that embed domain knowledge. These files are referenced by the agent's SYSTEM_PROMPT and can be loaded at runtime for deeper context.

Based on patterns from Anthropic's `financial-services` repo (see `references/financial-services-patterns.md`):

- **skills/domain-basics.md** — Market structure, key entities, rules, terminology
- **skills/strategies.md** — Analysis methodology, step-by-step processes, worked examples
- **skills/risk-management.md** — Safety rules, position sizing, exit criteria, psychological guardrails

Each skill file should:
- Be self-contained (work if printed and given to a human)
- Include a glossary of domain terms
- Contain at least one fully worked example
- Separate "what to do" from "how to get data"

For financial agents, `references/financial-tools.md` covers AKShare integration patterns:
- Market data (spot prices, option chains, greeks)
- Financial statements (income, balance sheet, cash flow)
- Financial ratios (PE, PB, ROE, ROA, margins, growth)
- Risk & P&L (option P&L calculator, strategy explainer)

## Important

- Always use `uv` for dependency management, never pip
- Always generate `config.toml` with sensible defaults, never hardcode LLM config
- Always include `.env.example` listing all required env vars
- Default to including Langfuse unless user explicitly opts out
- Default to SqliteSaver checkpointing for replay capability
- Do NOT generate a requirements.txt — use pyproject.toml with uv
- Always generate `infra/` with systemd services + setup.sh
- After scaffolding, run `bash infra/setup.sh` to enable services
- Run `sudo loginctl enable-linger $USER` on servers to persist services after logout

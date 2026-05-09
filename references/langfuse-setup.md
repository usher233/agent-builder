# Langfuse Observability Setup

Integration patterns for Langfuse tracing in LangGraph agents. Based on Langfuse docs and verified patterns.

## Quick Start

```python
# Install: uv add langfuse
from langfuse import get_client
from langfuse.langchain import CallbackHandler

# Initialize
langfuse = get_client()
langfuse_handler = CallbackHandler()
```

## config.toml

```toml
[langfuse]
public_key = "${LANGFUSE_PUBLIC_KEY}"
secret_key = "${LANGFUSE_SECRET_KEY}"
host = "https://cloud.langfuse.com"          # US region
# host = "https://api.us.langfuse.com"        # US alternative
# host = "https://api.eu.langfuse.com"        # EU region
# host = "http://localhost:3000"              # Self-hosted
enabled = true
environment = "development"
release = "0.1.0"
```

## LangGraph Integration

### Method 1: Pass handler in config.callbacks (Recommended)

```python
from langfuse.langchain import CallbackHandler

langfuse_handler = CallbackHandler()

async def run_agent():
    config = {
        "configurable": {"thread_id": thread_id},
        "callbacks": [langfuse_handler],
    }
    result = await graph.ainvoke({"messages": [msg]}, config=config)
```

Langfuse auto-captures:
- Each LangGraph node execution as a span
- LLM calls (token count, latency, model)
- Tool calls (name, arguments, result)
- Overall trace with input/output

### Method 2: Streaming with Callbacks

```python
async for chunk in graph.astream(
    {"messages": [msg]},
    config={"callbacks": [langfuse_handler], "configurable": {"thread_id": tid}},
    stream_mode="values",
):
    yield chunk
```

## Propagating Custom Attributes

```python
from langfuse import propagate_attributes

with propagate_attributes(
    session_id="session-123",
    user_id="user-456",
    tags=["production", "options-agent"],
):
    result = await graph.ainvoke(input, config)
```

## Adding Custom Metadata to Traces

```python
langfuse_handler = CallbackHandler(
    update_trace=True,  # auto-update trace with langchain metadata
)
```

Or manually:
```python
from langfuse import get_client

langfuse = get_client()
trace = langfuse.trace(name="options-analysis", user_id=user_id)
span = trace.span(name="fetch-market-data")
# ... do work ...
span.end()
trace.update(output=result)
langfuse.flush()  # ensure data is sent
```

## Scoring / Evaluation Traces

```python
from langfuse import get_client

langfuse = get_client()

# Score a specific trace
trace = langfuse.trace(id=trace_id)
trace.score(name="accuracy", value=0.95, comment="Good strategy selection")
```

## Self-Hosted Setup

```bash
# docker-compose.yml
# Uses: postgres, clickhouse (optional), redis (optional)
git clone https://github.com/langfuse/langfuse.git
cd langfuse
docker compose up -d

# Set config.toml host to localhost
# [langfuse]
# host = "http://localhost:3000"
```

## Key Patterns

1. **Always use `langfuse.flush()`** at end of short-lived processes (serverless) to ensure data is sent
2. **Session tracking**: Use `propagate_attributes(session_id=...)` to group traces by user session
3. **Environment segregation**: Use different API keys or `environment` config for dev/staging/prod
4. **Cost tracking**: Langfuse auto-calculates cost when model and token counts are available — pass the model name in LLM config
5. **Debugging**: Check `langfuse_handler` passed correctly — all LangChain/LangGraph events auto-captured

## Troubleshooting

- **No traces appear**: Check `enabled = true`, verify keys, call `langfuse.auth_check()`
- **Missing spans**: Ensure `callbacks` is in the `config` dict, not as a separate argument
- **Large traces truncated**: Set `LANGFUSE_MAX_EVENT_SIZE_BYTES` env var
- **Rate limiting**: Self-hosted has no rate limits; cloud tier limits apply

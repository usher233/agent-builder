# LangGraph Deep Patterns

Advanced LangGraph patterns for production agents. Complements the basic `langgraph-patterns.md` reference.

## Graph API Patterns (LangGraph 1.x)

### State Definition

```python
from typing import Annotated, TypedDict
from operator import add
from langgraph.graph.message import add_messages
from langchain_core.messages import BaseMessage

class AgentState(TypedDict):
    messages: Annotated[list[BaseMessage], add_messages]  # auto-merge messages
    intent: str
    results: Annotated[list[str], add]  # auto-append with operator.add
```

Key: Use `Annotated[type, reducer]` for fields that accumulate across nodes. `add_messages` is the special LangGraph reducer for chat messages.

### Node Patterns

**Async Nodes (recommended for I/O)**:
```python
async def router_node(state: AgentState) -> dict:
    """Return partial state update — merged with existing state."""
    return {"intent": "analyze"}
```

**Nodes with LLM (partial binding)**:
```python
from functools import partial

async def worker_node(state: AgentState, llm: BaseChatModel) -> dict:
    response = await llm.ainvoke(state["messages"])
    return {"messages": [response]}

# Build graph with:
builder.add_node("worker", partial(worker_node, llm=llm))
```

**Nodes with Runtime Context**:
```python
from langgraph.runtime import Runtime

async def context_aware_node(state: AgentState, runtime: Runtime[Context]) -> dict:
    user_id = runtime.context.user_id
    thread_id = runtime.execution_info.thread_id
    return {"user_id": user_id}
```

### Conditional Routing

```python
def route_after_node(state: AgentState) -> str:
    if state.get("intent") == "analyze":
        return "market_data"
    elif state.get("intent") == "teach":
        return "strategy_explainer"
    return "composer"  # default fallback

builder.add_conditional_edges("router", route_after_node)
```

### Entry/Exit

```python
from langgraph.graph import START, END

builder.set_entry_point("router")           # LangGraph 1.x: use string name
builder.add_edge("composer", END)
```

## Checkpointing Patterns

### AsyncSqliteSaver (Production)

```python
import aiosqlite
from langgraph.checkpoint.sqlite.aio import AsyncSqliteSaver

async def build_graph(llm):
    conn = await aiosqlite.connect("data/checkpoints.db")
    checkpointer = AsyncSqliteSaver(conn)
    # IMPORTANT: keep conn alive — no context manager
    return builder.compile(checkpointer=checkpointer)
```

**Warning**: Do NOT use `async with AsyncSqliteSaver.from_conn_string(...)` — the connection is closed when the context exits. Use manual `connect()` + pass connection.

### Checkpoint Replay

```python
# Get history
async for snapshot in graph.aget_state_history(config):
    print(snapshot)

# Get specific state
state = await graph.aget_state(config)

# Fork: modify state and continue
await graph.aupdate_state(
    config,
    values={"messages": [HumanMessage(content="new prompt")]},
)
forked = await graph.ainvoke(None, config)
```

## Streaming Patterns

### astream_events (Recommended for Web UI)

```python
async for event in graph.astream_events(
    {"messages": [msg]},
    config,
    version="v2",
):
    kind = event["event"]
    if kind == "on_chat_model_stream":
        yield event["data"]["chunk"].content
    elif kind == "on_tool_start":
        yield f"\n[Tool: {event['name']}]"
    elif kind == "on_tool_end":
        yield f"\n[Tool result received]"
```

### Event Types to Handle

| Event | Use |
|-------|-----|
| `on_chat_model_start` | LLM call starting |
| `on_chat_model_stream` | Token-level streaming |
| `on_chat_model_end` | LLM call complete (has token counts) |
| `on_tool_start` | Tool invocation starting |
| `on_tool_end` | Tool result available |
| `on_chain_start` | Node entering |
| `on_chain_end` | Node completing |

### Stream Modes

```python
# Values mode: full state after each step
graph.astream(input, config, stream_mode="values")

# Updates mode: only state changes per node
graph.astream(input, config, stream_mode="updates")

# Custom mode: get_stream_writer() for in-node streaming
from langgraph.config import get_stream_writer
def node(state):
    writer = get_stream_writer()
    writer({"status": "fetching market data..."})
    # ... do work ...
    writer({"status": "analysis complete"})
```

## Human-in-the-Loop

```python
from langgraph.types import Command, interrupt

def approval_node(state: AgentState) -> dict:
    """Pause and wait for human approval."""
    user_input = interrupt("Approve this trade analysis? (yes/no)")
    if user_input.lower() == "yes":
        return {"approved": True}
    return {"approved": False}

# In the graph:
builder.add_node("approval", approval_node)

# Invoke to trigger interrupt:
result = graph.invoke(input, config)
# result["__interrupt__"] contains the interrupt payload

# Resume with human input:
result = graph.invoke(Command(resume="yes"), config)
```

## Error Handling

```python
async def safe_node(state: AgentState) -> dict:
    try:
        result = await risky_operation(state)
        return {"results": [str(result)]}
    except Exception as e:
        return {"results": [f"Error: {e}"]}

# In graph: add fallback edge
builder.add_conditional_edges(
    "market_data",
    lambda s: "error_handler" if "Error" in str(s.get("results", [])[-1]) else "composer",
)
```

## Tool Binding Patterns

```python
# Bind tools to LLM (tools auto-converted to OpenAI-compatible schema)
llm_with_tools = llm.bind_tools(ALL_TOOLS)

# The LLM will respond with tool_calls when it needs data
response = await llm_with_tools.ainvoke(messages)

# Check for tool calls
if response.tool_calls:
    for tc in response.tool_calls:
        tool_fn = tool_map[tc["name"]]
        result = tool_fn.invoke(tc["args"])
        tool_messages.append(ToolMessage(content=str(result), tool_call_id=tc["id"]))
```

## Full Graph Building Pattern

```python
async def build_graph(llm: BaseChatModel, checkpoint_db: str = "data/checkpoints.db"):
    os.makedirs(os.path.dirname(checkpoint_db) or ".", exist_ok=True)

    builder = StateGraph(AgentState)

    builder.add_node("router", router_node)
    builder.add_node("worker", partial(worker_node, llm=llm))
    builder.add_node("tool_executor", partial(tool_executor_node, llm=llm))
    builder.add_node("composer", partial(composer_node, llm=llm))

    builder.set_entry_point("router")
    builder.add_edge("router", "worker")
    builder.add_conditional_edges("worker", route_after_worker)
    builder.add_conditional_edges("tool_executor", route_after_tool)
    builder.add_edge("composer", END)

    conn = await aiosqlite.connect(checkpoint_db)
    checkpointer = AsyncSqliteSaver(conn)
    return builder.compile(checkpointer=checkpointer)
```

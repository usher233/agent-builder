# LangGraph Patterns

## State Definition

Use `TypedDict` with `Annotated` reducers for message lists:

```python
from typing import TypedDict, Annotated
from langgraph.graph.message import add_messages
import operator

class AgentState(TypedDict):
    messages: Annotated[list[BaseMessage], add_messages]
    thread_id: str
    # Custom fields with reducer:
    # results: Annotated[list, operator.add]  # append-only
    # counter: Annotated[int, operator.add]   # numeric accumulator
```

### When to use `operator.add` vs custom reducer:
- `add_messages` — message lists (dedupes by ID, replaces same-ID messages)
- `operator.add` — simple lists (appends, no dedupe) or numeric counters
- Custom reducer — when you need merge logic (e.g., dict updates)

## Node Design

Each node is a single async function that reads state and returns a partial state update:

```python
async def my_node(state: AgentState) -> dict:
    """Single responsibility. Returns only the fields it updates."""
    result = await some_work(state["messages"][-1])
    return {"results": [result]}  # appended via operator.add
```

**Rules:**
- One node = one responsibility
- Nodes should be 20-80 lines
- If a node exceeds 100 lines, split it
- Nodes return `dict`, not modified state — LangGraph merges automatically
- Use `async def` for all nodes that do I/O (API calls, DB queries)

## Graph Construction

```python
from langgraph.graph import StateGraph, END
from langgraph.checkpoint.sqlite import SqliteSaver

builder = StateGraph(AgentState)

# Add nodes
builder.add_node("router", router_node)
builder.add_node("worker", worker_node)
builder.add_node("composer", composer_node)

# Edges and conditional routes
builder.set_entry_point("router")
builder.add_conditional_edges(
    "router",
    lambda state: "worker" if state["needs_work"] else "composer",
    {"worker": "worker", "composer": "composer"}
)
builder.add_edge("worker", "composer")
builder.add_edge("composer", END)

# Compile with checkpointer
import sqlite3
conn = sqlite3.connect("checkpoints.db", check_same_thread=False)
graph = builder.compile(checkpointer=SqliteSaver(conn))
```

## Conditional Routing

Always use a pure function for the routing decision:

```python
def route_after_router(state: AgentState) -> str:
    """Returns the next node name based on state."""
    last_msg = state["messages"][-1]
    if "analyze" in last_msg.content.lower():
        return "analyzer"
    elif "explain" in last_msg.content.lower():
        return "teacher"
    return "composer"

builder.add_conditional_edges("router", route_after_router, {
    "analyzer": "analyzer",
    "teacher": "teacher",
    "composer": "composer",
})
```

## Checkpointing and Replay

Every invocation creates a checkpoint. To replay:

```python
# Replay from a specific checkpoint
config = {"configurable": {"thread_id": "user_123"}}
past_state = graph.get_state(config)

# Fork: modify past state and re-execute
graph.update_state(config, {"decision": "overridden_value"})
new_result = await graph.ainvoke(None, config)  # resumes from modified state
```

## Streaming

Use `astream_events` for real-time output:

```python
async for event in graph.astream_events(state, config, version="v2"):
    kind = event["event"]
    if kind == "on_chat_model_stream":
        content = event["data"]["chunk"].content
        yield f"data: {content}\n\n"  # SSE
    elif kind == "on_tool_start":
        yield f"data: [TOOL] {event['name']}...\n\n"
```

## Langfuse Integration

```python
from langfuse.callback import CallbackHandler

langfuse_handler = CallbackHandler()
config = {
    "configurable": {"thread_id": thread_id},
    "callbacks": [langfuse_handler],
}
result = await graph.ainvoke(state, config)
```

Do NOT manually instrument — `CallbackHandler` captures all node timings, token counts, and tool calls automatically.

## Tool Definition

Use LangChain's `@tool` decorator for tools that the LLM can call:

```python
from langchain_core.tools import tool

@tool
async def get_option_chain(symbol: str) -> str:
    """Get the current option chain for an underlying symbol.
    Returns calls and puts with strike, expiry, bid, ask, greeks."""
    # implementation
    return formatted_result
```

Tools are bound to the LLM:

```python
llm_with_tools = llm.bind_tools(tools)
```

## Error Handling

Let errors propagate to the caller — don't swallow them in nodes. The FastAPI/Telegram layer handles user-facing error messages. Only catch errors that you can actually recover from (e.g., retry with backoff for API calls).

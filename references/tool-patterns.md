# Tool Patterns

## Pattern 1: API Wrapper Tool

For external data APIs (market data, weather, search):

```python
from langchain_core.tools import tool
import httpx

@tool
async def fetch_something(query: str) -> str:
    """Short description of what this tool does. Be specific about parameters."""
    async with httpx.AsyncClient() as client:
        resp = await client.get(f"https://api.example.com/data?q={query}")
        resp.raise_for_status()
        data = resp.json()
    return format_results(data)  # Return a string the LLM can read
```

**Rules:**
- Always use `httpx.AsyncClient` for HTTP calls
- Always call `raise_for_status()` to catch HTTP errors
- Return formatted strings, not raw JSON (the LLM needs readable text)
- Keep docstring specific — it's the only thing the LLM sees about the tool

## Pattern 2: File System Tool

For reading/writing local files:

```python
from pathlib import Path
from langchain_core.tools import tool

@tool
def read_project_file(path: str, max_lines: int = 200) -> str:
    """Read a file from the project directory. Use for checking existing code."""
    full_path = Path("data") / path
    if not full_path.exists():
        return f"File not found: {path}"
    content = full_path.read_text()
    lines = content.split("\n")[:max_lines]
    return "\n".join(lines)
```

## Pattern 3: MCP Connector

For tools that should be exposed via MCP (Model Context Protocol):

```python
# mcp_server.py
from mcp.server import Server, stdio_server
from mcp.types import Tool, TextContent

app = Server("my-data-server")

@app.list_tools()
async def list_tools():
    return [
        Tool(name="get_data", description="Fetch data by symbol",
             inputSchema={"type": "object", "properties": {"symbol": {"type": "string"}}})
    ]

@app.call_tool()
async def call_tool(name: str, arguments: dict):
    if name == "get_data":
        result = await fetch_data(arguments["symbol"])
        return [TextContent(type="text", text=str(result))]

if __name__ == "__main__":
    import asyncio
    asyncio.run(stdio_server(app))
```

Use MCP when the tool needs to be shared across multiple agents or accessed by external systems.

## Pattern 4: Database Tool

For SQL databases with connection pooling:

```python
import aiosqlite
from langchain_core.tools import tool

DB_PATH = "data/agent.db"

@tool
async def query_db(sql: str) -> str:
    """Run a read-only SQL query against the local database."""
    async with aiosqlite.connect(DB_PATH) as db:
        db.row_factory = aiosqlite.Row
        cursor = await db.execute(sql)
        rows = await cursor.fetchall()
        return format_rows(rows)
```

## Tool Organization

Group related tools in a single file. If a file exceeds 200 lines, split by domain:

```
src/tools/
├── data_fetchers.py    # API calls, web scraping
├── file_ops.py         # File system operations
└── calculations.py     # Math, analysis, computation
```

## Binding Tools to LLM

```python
tools = [fetch_something, read_project_file, query_db]
llm_with_tools = llm.bind_tools(tools)
```

The LLM will automatically decide when to call which tool based on the docstrings.

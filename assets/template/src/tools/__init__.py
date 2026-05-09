"""Domain-specific tools for this agent.

Add your custom LangChain @tool functions here. Export them via get_tools()
and they'll be merged with tool skills at startup in main.py.

For pre-built tools (web search, file system, data analysis, etc.),
copy them from the Agent Builder repo's skills/ directory into tool_skills/.
"""

from langchain_core.tools import tool


@tool
def example_tool(query: str) -> str:
    """An example tool — replace with your own. The LLM reads this docstring."""
    return f"Result for: {query}"


def get_tools():
    """Return domain-specific tools. Merged with skill tools at startup."""
    return [example_tool]

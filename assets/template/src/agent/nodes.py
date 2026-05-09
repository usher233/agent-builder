from langchain_core.language_models import BaseChatModel
from langchain_core.messages import HumanMessage, SystemMessage

from .state import AgentState

SYSTEM_PROMPT = """You are a helpful AI agent. Respond to the user's request accurately and concisely."""


async def router_node(state: AgentState) -> dict:
    """Entry point: logs the incoming request and forwards it."""
    last_msg = state["messages"][-1]
    return {"results": [f"Received: {last_msg.content[:100]}"]}


async def worker_node(state: AgentState, llm: BaseChatModel) -> dict:
    """Core processing node: sends messages to the LLM and gets a response."""
    messages = [SystemMessage(content=SYSTEM_PROMPT)] + state["messages"]
    response = await llm.ainvoke(messages)
    return {"messages": [response]}


async def composer_node(state: AgentState) -> dict:
    """Final node: formats the response. Override with domain-specific logic."""
    return {}

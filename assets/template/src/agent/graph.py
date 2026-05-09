import os
import aiosqlite
from functools import partial
from langgraph.graph import StateGraph, END
from langgraph.checkpoint.sqlite.aio import AsyncSqliteSaver
from langchain_core.language_models import BaseChatModel

from .state import AgentState
from .nodes import router_node, worker_node, composer_node


async def build_graph(llm: BaseChatModel, checkpoint_db: str = "data/checkpoints.db") -> StateGraph:
    """Build the LangGraph agent with async SQLite checkpointer for replay."""
    os.makedirs(os.path.dirname(checkpoint_db) or ".", exist_ok=True)

    builder = StateGraph(AgentState)

    # Nodes
    builder.add_node("router", router_node)
    builder.add_node("worker", partial(worker_node, llm=llm))
    builder.add_node("composer", composer_node)

    # Edges
    builder.set_entry_point("router")
    builder.add_edge("router", "worker")
    builder.add_edge("worker", "composer")
    builder.add_edge("composer", END)

    # Async SQLite checkpointer
    conn = await aiosqlite.connect(checkpoint_db)
    checkpointer = AsyncSqliteSaver(conn)
    return builder.compile(checkpointer=checkpointer)

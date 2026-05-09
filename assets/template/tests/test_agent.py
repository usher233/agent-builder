import pytest
from unittest.mock import AsyncMock, patch
from langchain_core.messages import HumanMessage
from src.agent.state import AgentState
from src.agent.graph import build_graph


@pytest.fixture
def mock_llm():
    llm = AsyncMock()
    llm.ainvoke.return_value = HumanMessage(content="Hello! How can I help?")
    return llm


def test_build_graph(mock_llm):
    graph = build_graph(mock_llm, checkpoint_db=":memory:")
    assert graph is not None


@pytest.mark.asyncio
async def test_graph_invoke(mock_llm):
    graph = build_graph(mock_llm, checkpoint_db=":memory:")
    state = {"messages": [HumanMessage(content="hi")], "thread_id": "test-1"}
    result = await graph.ainvoke(state)
    assert result["messages"][-1].content == "Hello! How can I help?"

"""CLI interface — simple terminal chat loop."""
import asyncio
import logging
import uuid

from langchain_core.messages import HumanMessage
from langfuse.callback import CallbackHandler

from src.config import Config

logger = logging.getLogger(__name__)


async def run(graph, cfg: Config) -> None:
    """Start an interactive CLI chat loop."""
    langfuse_handler = CallbackHandler(
        public_key=cfg.langfuse.public_key,
        secret_key=cfg.langfuse.secret_key,
        host=cfg.langfuse.host,
    )

    thread_id = str(uuid.uuid4())
    print(f"=== {cfg.llm.provider} agent (thread: {thread_id[:8]}...) ===")
    print("Type /exit to quit, /reset to clear history\n")

    loop = asyncio.get_event_loop()

    while True:
        try:
            user_input = await loop.run_in_executor(None, input, "> ")
        except (EOFError, KeyboardInterrupt):
            print("\nGoodbye.")
            break

        if user_input.lower() in ("/exit", "/quit"):
            print("Goodbye.")
            break

        if user_input.lower() == "/reset":
            thread_id = str(uuid.uuid4())
            print(f"New thread: {thread_id[:8]}...\n")
            continue

        if not user_input.strip():
            continue

        state = {
            "messages": [HumanMessage(content=user_input)],
            "thread_id": thread_id,
        }

        try:
            config = {
                "configurable": {"thread_id": thread_id},
                "callbacks": [langfuse_handler],
            }
            result = await graph.ainvoke(state, config)
            response = result["messages"][-1].content
            print(f"\n{response}\n")
        except Exception as e:
            logger.error("Error: %s", e)
            print(f"\nError: {e}\n")

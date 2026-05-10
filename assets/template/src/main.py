"""Agent entry point. Starts enabled interfaces based on config.toml."""
import asyncio
import logging

from src.config import Config, build_llm
from src.agent.graph import build_graph
from src.skills import load_tool_skills
from src.interfaces import run_interfaces

logging.basicConfig(level=logging.INFO, format="%(levelname)s | %(message)s")
logger = logging.getLogger(__name__)


async def main():
    cfg = Config.from_toml()
    llm = build_llm(cfg.llm)

    # Load enabled tool skills from config and bind to LLM
    skill_cfg = cfg.skills
    skill_tools = load_tool_skills(skill_cfg.enabled, skill_cfg)
    if skill_tools:
        llm = llm.bind_tools(skill_tools)
        logger.info("Tool skills loaded: %s (%d tools)", skill_cfg.enabled, len(skill_tools))

    graph = await build_graph(llm, checkpoint_db=cfg.agent.checkpoint_db)

    # Start all enabled interfaces (web, telegram, cli, etc.)
    await run_interfaces(graph, cfg)


if __name__ == "__main__":
    asyncio.run(main())

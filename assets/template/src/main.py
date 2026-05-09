"""Agent entry point. Starts web server and/or Telegram bot."""
import asyncio
import uvicorn
from src.config import Config, build_llm
from src.agent.graph import build_graph
from src.skills import load_tool_skills


async def main():
    cfg = Config.from_toml()
    llm = build_llm(cfg.llm)

    # Load enabled tool skills from config.toml and bind to LLM
    skill_tools = load_tool_skills(cfg.skills.enabled)
    if skill_tools:
        llm = llm.bind_tools(skill_tools)
        print(f"Tool skills loaded: {cfg.skills.enabled} ({len(skill_tools)} tools)")

    graph = build_graph(llm, checkpoint_db=cfg.agent.checkpoint_db)

    tasks = []

    # Web UI
    from src.web.app import create_app
    app = create_app(graph, cfg)
    config = uvicorn.Config(app, host=cfg.web.host, port=cfg.web.port)
    server = uvicorn.Server(config)
    tasks.append(server.serve())
    print(f"Web UI: http://{cfg.web.host}:{cfg.web.port}")

    # Telegram bot
    from src.bot.telegram import create_bot
    bot_app = create_bot(graph, cfg)
    tasks.append(bot_app.run_polling())
    print("Telegram bot started")

    await asyncio.gather(*tasks)


if __name__ == "__main__":
    asyncio.run(main())

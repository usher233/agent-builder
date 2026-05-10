"""FastAPI web interface with SSE streaming."""
import json
import uuid
import logging

from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse, StreamingResponse
from fastapi.templating import Jinja2Templates
from langchain_core.messages import HumanMessage
from langfuse.callback import CallbackHandler
from pathlib import Path

from src.config import Config

logger = logging.getLogger(__name__)
templates_dir = Path(__file__).parent / "templates"
templates = Jinja2Templates(directory=str(templates_dir))


def create_app(graph, cfg: Config) -> FastAPI:
    app = FastAPI(title=cfg.interfaces.web.get("title", "AI Agent"))
    langfuse_handler = CallbackHandler(
        public_key=cfg.langfuse.public_key,
        secret_key=cfg.langfuse.secret_key,
        host=cfg.langfuse.host,
    )

    @app.get("/", response_class=HTMLResponse)
    async def index(request: Request):
        return templates.TemplateResponse("index.html", {"request": request})

    @app.get("/api/chat")
    async def chat_stream(q: str, thread_id: str | None = None):
        thread_id = thread_id or str(uuid.uuid4())
        state = {"messages": [HumanMessage(content=q)], "thread_id": thread_id}

        async def event_stream():
            config = {
                "configurable": {"thread_id": thread_id},
                "callbacks": [langfuse_handler],
            }
            async for event in graph.astream_events(state, config, version="v2"):
                kind = event["event"]
                if kind == "on_chat_model_stream":
                    content = event["data"]["chunk"].content
                    if content:
                        yield f"data: {json.dumps({'content': content, 'thread_id': thread_id})}\n\n"
                elif kind == "on_tool_start":
                    yield f"data: {json.dumps({'tool': event['name'], 'thread_id': thread_id})}\n\n"
            yield f"data: {json.dumps({'done': True, 'thread_id': thread_id})}\n\n"

        return StreamingResponse(event_stream(), media_type="text/event-stream")

    @app.get("/api/threads/{thread_id}/replay")
    async def replay_thread(thread_id: str):
        """Replay a past conversation."""
        try:
            past_state = graph.get_state({"configurable": {"thread_id": thread_id}})
            messages = past_state.values.get("messages", [])
            return {
                "thread_id": thread_id,
                "messages": [{"role": type(m).__name__, "content": m.content} for m in messages],
                "checkpoint": str(past_state.next) if past_state.next else None,
            }
        except Exception:
            return {"error": "Thread not found", "thread_id": thread_id}

    return app


async def run(graph, cfg: Config) -> None:
    """Start the web interface."""
    import uvicorn

    web_cfg = cfg.interfaces.web
    host = web_cfg.get("host", "0.0.0.0")
    port = web_cfg.get("port", 8080)

    app = create_app(graph, cfg)
    config = uvicorn.Config(app, host=host, port=port)
    server = uvicorn.Server(config)
    logger.info("Web UI: http://%s:%s", host, port)
    await server.serve()

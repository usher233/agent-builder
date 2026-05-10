"""Interface dispatcher — starts enabled interfaces from config.toml."""
import asyncio
import importlib
import logging

from src.config import Config

logger = logging.getLogger(__name__)

INTERFACE_MAP = {
    "web": "src.interfaces.web",
    "telegram": "src.interfaces.telegram",
    "cli": "src.interfaces.cli",
}


async def run_interfaces(graph, cfg: Config) -> None:
    """Start all enabled interfaces concurrently."""
    enabled = cfg.interfaces.enabled
    tasks = []

    for name in enabled:
        module_path = INTERFACE_MAP.get(name)
        if module_path is None:
            logger.warning("Unknown interface: %s (available: %s)", name, list(INTERFACE_MAP))
            continue
        try:
            module = importlib.import_module(module_path)
            task = asyncio.create_task(module.run(graph, cfg))
            tasks.append(task)
            logger.info("Interface started: %s", name)
        except ImportError as e:
            logger.warning("Interface '%s' not installed. Missing deps? %s", name, e)
        except Exception as e:
            logger.error("Failed to start interface '%s': %s", name, e)

    if not tasks:
        logger.warning("No interfaces enabled. Add interfaces to [interfaces] in config.toml")
        return

    await asyncio.gather(*tasks)

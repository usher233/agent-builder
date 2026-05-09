"""
Skill system for AI agents.

Two kinds of skills:
1. Domain skills (skills/*.md) — Markdown files with domain knowledge, loaded as LLM context at runtime.
   Pattern from Anthropic's financial-services repo: load skill → inject as system context → execute.

2. Tool skills (tool_skills/*.py) — Pre-built Python tool modules from the Agent Builder marketplace.
   Each exposes get_tools() -> list. Enable in config.toml → auto-bound to LLM.

Usage:
    from src.skills import load_tool_skills, load_domain_skill

    # Load tool skills at startup (based on config.toml)
    tools = load_tool_skills(cfg.skills.enabled)
    llm = llm.bind_tools(tools)

    # Load domain skill at runtime (based on user intent)
    context = load_domain_skill("strategies")
"""

import importlib
import logging
from pathlib import Path

logger = logging.getLogger(__name__)

# Map skill names → Python import paths for tool skills
_TOOL_SKILL_REGISTRY = {
    "web-search": "tool_skills.web_search",
    "file-system": "tool_skills.file_system",
    "data-analysis": "tool_skills.data_analysis",
    "code-interpreter": "tool_skills.code_interpreter",
    "financial-data": "tool_skills.financial_data",
}

# Map intent keywords → domain skill files
DOMAIN_SKILL_DIR = Path("skills")
INTENT_SKILL_MAP = {
    "analyze": "strategies.md",
    "teach": "strategies.md",
    "basics": "domain-basics.md",
    "risk": "risk-management.md",
    "fundamental": "domain-basics.md",
}


def load_tool_skills(enabled: list[str]) -> list:
    """Import enabled tool skill modules and return their combined LangChain tools.

    Each tool skill is a Python package under tool_skills/ that exports get_tools().
    Copy them from the Agent Builder repo's skills/ directory, or write your own.
    """
    tools = []
    for name in enabled:
        if name not in _TOOL_SKILL_REGISTRY:
            logger.warning("Unknown tool skill: %s (available: %s)", name, list(_TOOL_SKILL_REGISTRY))
            continue
        try:
            module = importlib.import_module(_TOOL_SKILL_REGISTRY[name])
            skill_tools = module.get_tools()
            tools.extend(skill_tools)
            logger.info("Tool skill loaded: %s (%d tools)", name, len(skill_tools))
        except ImportError:
            logger.warning("Tool skill '%s' not installed. Missing dependencies?", name)
        except Exception as e:
            logger.error("Failed to load tool skill '%s': %s", name, e)
    return tools


def load_domain_skill(name_or_path: str) -> str:
    """Load a domain knowledge skill file and return its content as a string.

    Pass the result as system context to the LLM:
        context = load_domain_skill("strategies")
        messages = [SystemMessage(content=context)] + state["messages"]
    """
    # Try as a known name first
    filename = name_or_path if name_or_path.endswith(".md") else f"{name_or_path}.md"
    path = DOMAIN_SKILL_DIR / filename

    if not path.exists():
        # Try direct path
        path = Path(name_or_path)
    if not path.exists():
        logger.warning("Domain skill not found: %s", name_or_path)
        return ""

    content = path.read_text(encoding="utf-8")
    logger.info("Domain skill loaded: %s (%d chars)", path.name, len(content))
    return content


def load_skill_for_intent(intent: str) -> str:
    """Load the best domain skill file for a given user intent.

    Pattern from Anthropic's financial-services repo:
    User Request → Router (determine intent) → Load Skill → Execute → Format Output
    """
    filename = INTENT_SKILL_MAP.get(intent, "domain-basics.md")
    path = DOMAIN_SKILL_DIR / filename
    if not path.exists():
        return ""
    return path.read_text(encoding="utf-8")

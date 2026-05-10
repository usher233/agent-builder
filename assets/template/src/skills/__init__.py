"""
Skill system for AI agents.

Two kinds of skills:
1. Domain skills (skills/*.md) — Markdown files with domain knowledge, loaded as LLM context at runtime.
2. Tool skills (tool_skills/*/) — Pre-built Python tool modules from the Agent Builder marketplace.
   Each exposes get_tools() and get_default_config(). Enable in config.toml → auto-bound to LLM.

Usage:
    from src.skills import load_tool_skills, load_domain_skill

    tools = load_tool_skills(cfg.skills.enabled, cfg.skills)
    llm = llm.bind_tools(tools)

    context = load_domain_skill("strategies")
"""

import importlib
import logging
from pathlib import Path

logger = logging.getLogger(__name__)

TOOL_SKILL_PACKAGES = {
    "web-search": "tool_skills.web_search",
    "file-system": "tool_skills.file_system",
    "data-analysis": "tool_skills.data_analysis",
    "code-interpreter": "tool_skills.code_interpreter",
    "financial-data": "tool_skills.financial_data",
}

DOMAIN_SKILL_DIR = Path("skills")


def load_tool_skills(enabled: list[str], skills_cfg=None) -> list:
    """Import enabled tool skill modules and return their combined LangChain tools.

    Each tool skill is a Python package under tool_skills/ that exports:
    - get_tools() -> list of LangChain tools
    - get_default_config() -> dict of config defaults

    Copy them from the Agent Builder repo's skills/ directory, or write your own.
    """
    tools = []
    for name in enabled:
        pkg = TOOL_SKILL_PACKAGES.get(name)
        if pkg is None:
            logger.warning("Unknown tool skill: %s (available: %s)", name, list(TOOL_SKILL_PACKAGES))
            continue
        try:
            module = importlib.import_module(pkg)
            skill_tools = module.get_tools()

            # Apply user config overrides if available
            if skills_cfg is not None:
                user_cfg = skills_cfg.get_skill_config(name)
                if user_cfg and hasattr(module, "configure"):
                    module.configure(user_cfg)

            tools.extend(skill_tools)
            logger.info("Tool skill loaded: %s (%d tools)", name, len(skill_tools))
        except ImportError:
            logger.warning("Tool skill '%s' not installed. Missing dependencies?", name)
        except Exception as e:
            logger.error("Failed to load tool skill '%s': %s", name, e)
    return tools


def list_domain_skills() -> list[str]:
    """List available domain skill files in the skills/ directory."""
    if not DOMAIN_SKILL_DIR.exists():
        return []
    return sorted(
        f.name for f in DOMAIN_SKILL_DIR.glob("*.md")
    )


def load_domain_skill(name_or_path: str) -> str:
    """Load a domain knowledge skill file and return its content.

    Pass the result as system context to the LLM:
        context = load_domain_skill("strategies")
        messages = [SystemMessage(content=context)] + state["messages"]
    """
    filename = name_or_path if name_or_path.endswith(".md") else f"{name_or_path}.md"
    path = DOMAIN_SKILL_DIR / filename

    if not path.exists():
        path = Path(name_or_path)
    if not path.exists():
        logger.warning("Domain skill not found: %s", name_or_path)
        return ""

    content = path.read_text(encoding="utf-8")
    logger.info("Domain skill loaded: %s (%d chars)", path.name, len(content))
    return content


def load_all_domain_skills() -> str:
    """Load and concatenate all domain skill files."""
    parts = []
    for name in list_domain_skills():
        content = load_domain_skill(name)
        if content:
            parts.append(content)
    return "\n\n---\n\n".join(parts)

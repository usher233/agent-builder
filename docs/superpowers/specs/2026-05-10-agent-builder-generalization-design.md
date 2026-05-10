# Agent Builder Generalization Design

## Goal

Make the Agent Builder Skill more general-purpose and modular:
1. Replace finance-domain-specific language with generic wording throughout
2. Modularize the Interface layer (Web, Telegram → selectable, add CLI)
3. Modularize the Tool Skill layer (dynamic config, no hardcoded skill sections)

## Interface Layer

### Config change

Replace hardcoded `[web]` and `[telegram]` sections with a unified `[interfaces]` block:

```toml
[interfaces]
enabled = ["web", "telegram"]

[interfaces.web]
host = "0.0.0.0"
port = 8080

[interfaces.telegram]
bot_token = "${TELEGRAM_BOT_TOKEN}"
```

### Directory change

Merge `src/web/` + `src/bot/` into `src/interfaces/`:

```
src/interfaces/
├── __init__.py      # run_interfaces(graph, cfg) — dispatcher
├── web.py           # FastAPI + SSE
├── telegram.py      # python-telegram-bot
└── cli.py           # NEW: simple CLI loop
```

Each module exposes `async def run(graph, cfg) -> None`.

### main.py change

```python
async def main():
    ...
    await run_interfaces(graph, cfg)  # single call, iterates enabled list
```

## Tool Skill Layer

### Config change

Delete all hardcoded `[skills.xxx]` sections. Replace with:

```toml
[skills]
enabled = ["web-search", "file-system"]

[skills.config.web-search]
tavily_api_key = "${TAVILY_API_KEY}"

# Any [skills.config.<name>] section is optional — skills have defaults
```

### Each skill module adds get_default_config()

```python
def get_default_config():
    return {"tavily_api_key": "", "max_results": 5}
```

### config.py change

`SkillsConfig` gains a `config: dict[str, dict]` field — skill name to user overrides.

### skills/__init__.py change

- Remove hardcoded `INTENT_SKILL_MAP` (finance-specific intent→file mapping)
- Replace with generic: scan `skills/` directory for all `.md` files, match by filename

## Language Generalization

### SKILL.md
- Domain skills section: "market/domain mechanics" → "domain knowledge"
- Remove finance-specific examples (trading, A-share, position sizing)
- Wizard mode agent types: add more general options
- Template file comments: remove finance-biased placeholder text

### Template skill files (domain-basics.md, strategies.md, risk-management.md)
- Comments: "market structure" → "domain knowledge"
- "position sizing" → "resource limits"
- Keep the 3-file structure but make placeholders completely generic

### Reference docs
- `financial-services-patterns.md` and `financial-tools.md`: keep as optional references, not core
- No changes to other 6 reference files

## Files Changed

| File | Change |
|------|--------|
| `SKILL.md` | Generic wording, wizard options expanded |
| `assets/template/config.toml` | `[interfaces]` + dynamic `[skills]` |
| `assets/template/pyproject.toml` | Dependencies gated by interface selection |
| `assets/template/src/main.py` | Use `run_interfaces()` |
| `assets/template/src/config.py` | `InterfacesConfig`, `SkillsConfig` with dynamic dict |
| `assets/template/src/skills/__init__.py` | Remove `INTENT_SKILL_MAP`, generic file loader |
| `assets/template/src/interfaces/__init__.py` | NEW: dispatcher |
| `assets/template/src/interfaces/web.py` | Moved from `src/web/app.py` |
| `assets/template/src/interfaces/telegram.py` | Moved from `src/bot/telegram.py` |
| `assets/template/src/interfaces/cli.py` | NEW: simple CLI |
| `assets/template/skills/*.md` | Generic placeholder comments |
| `skills/*/tools.py` (5 files) | Add `get_default_config()` |
| `skills/*/SKILL.md` (5 files) | Generic descriptions |
| `README.md` | Reflect changes |

## What Does NOT Change

- LangGraph patterns (graph.py, nodes.py, state.py)
- Langfuse integration
- systemd + Docker Compose infrastructure
- Tool skill implementations (only add get_default_config)
- 6 non-financial reference docs
- MIT license

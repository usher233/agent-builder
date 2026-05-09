# Skills Marketplace

Pre-built skill modules for your AI agents. Two types of skills coexist:

## Tool Skills (`skills/*/`)
**Python modules** with LangChain-compatible tools. Each is a self-contained package — copy it into your agent's `tool_skills/` directory and enable in `config.toml`.

```toml
[skills]
enabled = ["web-search", "data-analysis"]
```

| Skill | Tools | Requires |
|-------|-------|----------|
| **web-search** | `search_web`, `fetch_page` | `tavily-python`, `TAVILY_API_KEY` |
| **file-system** | `read_file`, `write_file`, `list_dir` | None (stdlib) |
| **data-analysis** | `analyze_csv`, `create_chart` | `pandas`, `plotly` |
| **code-interpreter** | `run_python`, `install_package` | None (stdlib) |
| **financial-data** | `get_spot`, `get_financials`, `get_option_chain`, `get_etf_holdings` | `akshare` |

## Domain Skills (`assets/template/skills/*.md`)
**Markdown files** loaded as LLM system context at runtime. These teach the agent domain knowledge — methodology, terminology, and worked examples.

Pattern from Anthropic's `financial-services` repo:
```
User Request → Router (determine intent) → Load Skill → Inject as context → Execute → Format Output
```

| Template | Purpose |
|----------|---------|
| **domain-basics.md** | Market structure, key entities, rules, glossary |
| **strategies.md** | Step-by-step methodology, decision frameworks, worked examples |
| **risk-management.md** | Safety rules, exit criteria, forbidden actions |

## Creating Your Own

### Tool Skill
```
skills/my-skill/
├── SKILL.md        # Claude Code skill definition
├── __init__.py     # exports get_tools()
└── tools.py        # LangChain @tool implementations
```

### Domain Skill
Just drop a `.md` file in your agent's `skills/` directory. Include:
- Glossary of domain terms
- At least one fully worked example
- Separate "what to do" from "how to get data"

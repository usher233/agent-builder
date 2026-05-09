# Financial Services Agent Patterns

Patterns extracted from Anthropic's `financial-services` repository. Adapted for independent developers building financial agents.

## Architecture Pattern: Vertical Plugins + Skills

The repo organizes financial expertise into `vertical-plugins/` — each vertical bundles skills (markdown files containing domain knowledge + instructions) and MCP connectors for data access.

```
vertical-plugins/
├── financial-analysis/skills/   # DCF, comps, LBO, 3-statement models
├── equity-research/skills/      # Earnings, initiation, morning notes, screens
├── investment-banking/skills/   # Pitch books, CIMs, buyer lists, merger models
├── private-equity/skills/       # Deal sourcing, DD, IC memos, portfolio monitoring
├── wealth-management/skills/    # Client reviews, financial plans, rebalancing
└── fund-admin/skills/           # GL recon, accruals, NAV tie-out
```

**Key insight**: Each skill is a self-contained markdown file that teaches the model:
1. **Domain context** — what this analysis is, who uses it, when to apply it
2. **Step-by-step process** — the exact methodology
3. **Conventions** — industry-standard formats, calculations, terminology
4. **Examples** — worked examples the model can reference

## Skill File Conventions

From examining the repo's skills, the effective patterns are:

### 1. Structured Methodology

Skills define a clear sequence the model follows:
```
1. Gather data (from tools/sources)
2. Perform calculations (defined formulas)
3. Format output (specific templates)
4. Review and validate (checks and balances)
```

### 2. Domain Knowledge Embedded in Instructions

Instead of referencing external data, skills embed the domain expertise directly:
- Formula definitions (WACC = E/V × Re + D/V × Rd × (1-t))
- Industry benchmarks (typical multiples by sector)
- Common pitfalls (don't double-count, watch for non-recurring items)
- Terminology glossaries

### 3. Output Templates

Skills specify exact output formats:
```markdown
## Output Format
# [Company Name] — [Analysis Type]
## Executive Summary (3-5 bullet points)
## Key Metrics
| Metric | Value | Industry Avg | Implication |
## Risks and Considerations
## Recommendation (with price target if applicable)
```

### 4. Separation of Concerns

- **Skills**: Domain knowledge + methodology (what to do)
- **MCP Connectors**: Data access (how to get data)
- **Tools**: Computation (how to calculate)

This separation means skills are reusable across different data providers — swap the MCP connector, keep the skill.

## Applying to A-Share Options Agent

Our agent already follows this pattern:

| Anthropic Pattern | Our Implementation |
|---|---|
| Vertical skills (`.md` files) | `skills/options-strategies.md`, `skills/a-share-market-basics.md`, `skills/risk-management.md` |
| MCP connectors for data | `src/tools/market_data.py`, `src/tools/financials.py` (AKShare wrappers) |
| Output templates | SYSTEM_PROMPT with structured guidelines |
| Domain knowledge embedded | Strategy reference with A-share specifics |

## Key Takeaways for Agent-Builder Skill

When scaffolding a new financial agent:

1. **Create a `skills/` folder** with at least 2-3 markdown files covering:
   - Domain mechanics (market structure, contract specs for trading agents)
   - Strategy/analysis methodology (step-by-step processes)
   - Risk management (specific to the domain and account size)

2. **Make skills self-contained** — they should work if printed out and given to a human analyst

3. **Include Chinese terminology** for A-share/China-market agents — bilingual domain knowledge is critical

4. **Always include a glossary** — domain-specific terms mapped to plain language explanations

5. **Write worked examples** — a single worked example is worth 10 pages of abstract rules

6. **Separate "what" from "how"**:
   - Skills = what to do (domain knowledge)
   - Tools = how to get data (API wrappers)
   - Agent nodes = how to execute (LangGraph nodes)

## MCP Integration Pattern (from the repo)

```python
# mcp_financial_server.py — centralize data access
from mcp.server import Server, stdio_server
from mcp.types import Tool, TextContent

app = Server("financial-data")

@app.list_tools()
async def list_tools():
    return [
        Tool(name="get_financial_statements", description="..."),
        Tool(name="get_market_data", description="..."),
    ]

@app.call_tool()
async def call_tool(name: str, arguments: dict):
    # Route to data providers (AKShare, Wind, etc.)
    ...
```

This pattern allows multiple agents to share the same data access layer. For independent developers, this can start as direct tool functions and graduate to MCP when you have multiple agents.

## Skill-Driven Agent Design Pattern

From the repo's approach, the most powerful pattern is:

```
User Request → Router (pick skill) → Load Skill Context → Execute Methodology → Format Output
```

In LangGraph:
```python
builder.add_node("router", route_to_skill)
builder.add_node("load_skill", partial(load_skill, skill_dir="skills/"))
builder.add_node("execute", execute_with_skill_context)
builder.add_node("composer", format_output)
```

Where `load_skill` reads the relevant .md file and injects it as system context for the LLM. This is how Anthropic's agents apply domain-specific expertise — they load the right skill file for the task.

For our A-share agent, we can implement this as:
```python
async def load_skill_node(state: AgentState) -> dict:
    """Load relevant skill file based on intent."""
    skill_map = {
        "teach": "skills/options-strategies.md",
        "analyze": "skills/a-share-market-basics.md",
        "fundamental": "skills/risk-management.md",
    }
    skill_path = skill_map.get(state.get("intent"), "skills/options-strategies.md")
    with open(skill_path) as f:
        skill_content = f.read()
    return {"skill_context": skill_content}
```

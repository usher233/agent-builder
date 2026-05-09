<div align="center">

<img src="https://img.shields.io/badge/LangGraph-0.3+-green?style=for-the-badge&logo=langchain" alt="LangGraph">
<img src="https://img.shields.io/badge/Python-3.12+-blue?style=for-the-badge&logo=python" alt="Python">
<img src="https://img.shields.io/badge/license-MIT-brightgreen?style=for-the-badge" alt="License">
<img src="https://img.shields.io/badge/uv-package%20manager-purple?style=for-the-badge&logo=python" alt="uv">
<img src="https://img.shields.io/badge/Docker-ready-2496ED?style=for-the-badge&logo=docker" alt="Docker">

<br><br>

<h1>🏗️ Agent Builder</h1>

<h3>一个 Claude Code Skill。一句话生成一个可直接部署的生产级 AI Agent。</h3>
<h3><em>One sentence → Production-ready AI agent. Deploy to prod with one bash script.</em></h3>

<br>

<p>
  <b>中文</b> &nbsp;|&nbsp;
  <a href="#english">English</a>
</p>

<br>

---

</div>

> ⚠️ **Disclaimer / 免责声明**：本项目纯属个人业余兴趣爱好，与本人任职公司无关。This is a personal hobby project, not affiliated with or endorsed by my employer.

## 🚀 这是什么？

**Agent Builder** 是 Claude Code 的一个超级 Skill。你只需要告诉 Claude 你想要什么——比如 "帮我做一个股票分析机器人"——它就会在 **30 秒内** 生成一个完整的、可以直接 `systemctl start` 的生产级 Python 项目。

不是 demo，不是 hello-world，是真正的生产代码。**含 systemd 部署、Docker Compose 基础设施、Langfuse 全链路追踪、Telegram + Web 双界面。**

- ✅ **LangGraph 1.x 状态图** — 条件路由、检查点回放、流式输出、Human-in-the-Loop
- ✅ **多 LLM 热插拔** — DeepSeek / Anthropic / OpenAI / 任何兼容接口，一行配置切换
- ✅ **FastAPI + SSE + HTMX** — 流式聊天界面，不需要重 JS 框架
- ✅ **Telegram Bot** — 开箱即用，每条对话独立 thread_id，支持回放
- ✅ **Langfuse 全链路追踪** — 自动捕获 node、LLM call、tool call。零埋点
- ✅ **Skill 双系统** — 工具技能（Python 模块）+ 领域技能（.md 知识库），从 Anthropic financial-services 项目提炼
- ✅ **systemd 部署** — `infra/setup.sh` 一键安装 systemd 服务，重启自启，崩溃自动恢复
- ✅ **Docker Compose** — Langfuse 自托管栈（6 容器），一行命令拉起来
- ✅ **uv 包管理** — 极速安装，不搞 requirements.txt

<br>

## 📸 30 秒生成一个 Agent

```bash
# 你只需要说一句话
"Build me a crypto trading analyst agent with Telegram bot"

# Claude Code 会在 30 秒内生成完整项目：
my-crypto-analyst/
├── pyproject.toml              # uv 依赖管理
├── config.toml                 # LLM / Langfuse / Skills / Telegram 配置
├── .env.example
├── Dockerfile
├── skills/                     # 领域知识 .md 文件（Agent 运行时加载）
│   ├── domain-basics.md        # 市场机制、关键实体、术语表
│   ├── strategies.md           # 分析方法论、步骤、案例
│   └── risk-management.md      # 安全规则、退出条件、禁区
├── tool_skills/                # 从 Skills 市场拷贝的工具模块（可选）
│   └── ...
├── infra/                      # 部署基础设施
│   ├── docker-compose.langfuse.yml  # Langfuse 自托管（6 容器）
│   ├── langfuse.service             # systemd unit
│   ├── <agent-name>.service         # systemd unit
│   └── setup.sh                     # 一键安装脚本
├── src/
│   ├── main.py                 # 入口：启动 Web + Bot + 加载 Skills
│   ├── config.py               # 配置解析 + LLM 工厂
│   ├── skills/                 # Skill 加载器（工具 + 领域）
│   │   └── __init__.py         # load_tool_skills() + load_domain_skill()
│   ├── agent/
│   │   ├── graph.py            # LangGraph StateGraph + SqliteSaver
│   │   ├── nodes.py            # 节点逻辑（含 skill 加载节点）
│   │   └── state.py            # TypedDict 状态定义
│   ├── tools/
│   │   └── __init__.py         # 领域工具
│   ├── web/
│   │   ├── app.py              # FastAPI + SSE 流式 + 回放 API
│   │   └── templates/
│   │       └── index.html
│   └── bot/
│       └── telegram.py         # python-telegram-bot
└── tests/
    └── test_agent.py
```

**然后直接部署：**
```bash
uv sync
bash infra/setup.sh
# Web UI: http://0.0.0.0:8080
# Langfuse: http://localhost:3000
# Telegram Bot: 已启动
# 重启后自动启动：✅
```

<br>

## 🎯 核心亮点

<table>
<tr>
<td width="33%">

### 🔌 多 LLM 热插拔
一行配置，切换 AI 供应商。不用改代码。

```toml
[llm]
provider = "deepseek"  # ← 改这里
# provider = "anthropic"
# provider = "openai"
model = "deepseek-v4-pro"
```

</td>
<td width="33%">

### 🧠 Skill 双系统
工具箱 + 知识库。从 Anthropic 金融 AI 项目提炼。

```python
# 工具技能（Python 模块）
tools = load_tool_skills(["web-search", "data-analysis"])

# 领域技能（.md 知识库）
context = load_skill_for_intent("analyze")
```

</td>
<td width="33%">

### 🏗️ 一键生产部署
systemd 管理进程，崩溃自动重启。

```bash
bash infra/setup.sh
systemctl --user status my-agent
journalctl --user -u my-agent -f
```

</td>
</tr>
</table>

<br>

## 🎨 两种模式

### ⚡ 脚手架模式
> "Build me a customer support bot with web UI and Langfuse"

30 秒生成。直接部署。

### 🧙 向导模式
> "I want to build an AI agent but not sure how..."

一步步引导：Agent 类型 → LLM → 界面 → 可观测性 → 持久化 → 工具。每一步都有推荐和解释。

<br>

## 🧩 Skills 市场

Agent Builder 附带 5 个预制工具技能，直接复制到项目里就能用：

| 技能 | 工具 | 依赖 |
|------|------|------|
| **web-search** | `search_web`, `fetch_page` | Tavily API |
| **file-system** | `read_file`, `write_file`, `list_dir` | 无 |
| **data-analysis** | `analyze_csv`, `create_chart` | pandas, plotly |
| **code-interpreter** | `run_python`, `install_package` | 无 |
| **financial-data** | `get_spot`, `get_financials`, `get_option_chain`, `get_etf_holdings` | akshare |

另有 3 个领域技能模板（`skills/domain-basics.md`、`strategies.md`、`risk-management.md`），Agent 在运行时根据意图自动加载——这是 Anthropic financial-services 项目的核心模式。

<br>

## 📦 基础设施

```
┌─────────────────────────────────┐
│ systemd --user                   │
│  ┌─ langfuse.service ──────────┐ │
│  │  docker compose up -d        │ │
│  │  ├─ postgres                 │ │
│  │  ├─ clickhouse               │ │
│  │  ├─ redis                    │ │
│  │  ├─ minio                    │ │
│  │  ├─ langfuse-web (:3000)     │ │
│  │  └─ langfuse-worker          │ │
│  └─────────────────────────────┘ │
│           │ depends on            │
│           ▼                       │
│  ┌─ agent.service ─────────────┐ │
│  │  python -m src.main          │ │
│  │  ├─ FastAPI (:8080)          │ │
│  │  └─ Telegram Bot (polling)   │ │
│  └─────────────────────────────┘ │
└─────────────────────────────────┘
```

```bash
# 部署命令
bash infra/setup.sh

# 日常运维
systemctl --user status my-agent
journalctl --user -u my-agent -f
systemctl --user restart my-agent

# 服务器保活（SSH 断开后服务不停止）
sudo loginctl enable-linger $USER
```

<br>

## 📚 参考文档

| 文档 | 内容 |
|------|------|
| [`SKILL.md`](SKILL.md) | 核心 Skill 定义，完整脚手架工作流 |
| [`references/llm-config.md`](references/llm-config.md) | 多 LLM 配置规范 |
| [`references/langgraph-patterns.md`](references/langgraph-patterns.md) | LangGraph 基础：状态、路由、检查点 |
| [`references/langgraph-patterns-deep.md`](references/langgraph-patterns-deep.md) | LangGraph 进阶：流式、Human-in-the-Loop、错误处理 |
| [`references/langfuse-setup.md`](references/langfuse-setup.md) | Langfuse 集成：云端/自托管、属性传播、评分 |
| [`references/tool-patterns.md`](references/tool-patterns.md) | 4 种工具模式：API 封装、文件系统、MCP、数据库 |
| [`references/infrastructure.md`](references/infrastructure.md) | systemd + Docker Compose 部署指南 |
| [`references/financial-tools.md`](references/financial-tools.md) | AKShare 金融数据集成参考 |
| [`references/financial-services-patterns.md`](references/financial-services-patterns.md) | Anthropic 金融 AI 项目架构解析 |

<br>

## 🔧 技术栈

| 技术 | 用途 |
|------|------|
| **LangGraph 1.x** | Agent 状态图引擎 |
| **LangChain** | LLM 抽象层 + 工具绑定 |
| **FastAPI** | Web API + SSE 流式传输 |
| **HTMX** | 前端交互（无需重型 JS 框架） |
| **python-telegram-bot** | Telegram Bot 接口 |
| **Langfuse** | LLM 可观测性平台（云端 + 自托管） |
| **systemd** | 进程守护、自动重启、开机自启 |
| **Docker Compose** | Langfuse 自托管栈 |
| **uv** | Python 包管理器 |
| **Docker** | 容器化部署 |

<br>

---

<br>

<div align="center">

<a name="english"></a>

<h1>🏗️ Agent Builder</h1>

<h3>One sentence → Production-ready AI agent. Deploy to prod with one bash script.</h3>

<br>

<p>
  <a href="#中文">中文</a> &nbsp;|&nbsp;
  <b>English</b>
</p>

<br>

</div>

> ⚠️ **Disclaimer**：This is a personal hobby project, not affiliated with or endorsed by my employer. / 本项目纯属个人业余兴趣爱好，与本人任职公司无关。

## 🚀 What Is This?

**Agent Builder** is a Claude Code skill. Tell Claude what you want — "build me a stock analysis bot" — and it generates a complete, deployment-ready Python project in **under 30 seconds**.

We're talking `systemctl start` ready. Not a demo. Not a hello-world. Production code.

- ✅ **LangGraph 1.x StateGraph** — conditional routing, checkpoint replay, streaming, Human-in-the-Loop
- ✅ **Multi-LLM Hot-Swap** — DeepSeek / Anthropic / OpenAI / custom. One config line.
- ✅ **FastAPI + SSE + HTMX** — streaming chat UI, no heavy JS frameworks
- ✅ **Telegram Bot** — per-chat thread isolation with replay support
- ✅ **Langfuse Tracing** — auto-capture nodes, LLM calls, tool calls. Zero instrumentation.
- ✅ **Dual Skill System** — Tool skills (Python modules) + Domain skills (.md knowledge base), distilled from Anthropic's financial-services repo
- ✅ **systemd Deployment** — `infra/setup.sh` one-shot: install services, enable auto-start, crash recovery
- ✅ **Docker Compose** — Langfuse self-hosted stack (6 containers), single command
- ✅ **uv Package Manager** — lightning fast. No requirements.txt nonsense.

<br>

## 📸 30 Seconds to a Complete Agent

```bash
# You say:
"Build me a crypto trading analyst agent with Telegram bot"

# Claude Code generates in 30 seconds:
my-crypto-analyst/
├── pyproject.toml              # uv dependency management
├── config.toml                 # LLM / Langfuse / Skills / Telegram config
├── .env.example
├── Dockerfile
├── skills/                     # Domain knowledge .md files (loaded at runtime)
│   ├── domain-basics.md        # Market mechanics, entities, glossary
│   ├── strategies.md           # Methodology, step-by-step, worked examples
│   └── risk-management.md      # Safety rules, exit criteria, guardrails
├── tool_skills/                # Copied from Skills Marketplace (optional)
│   └── ...
├── infra/                      # Deployment infrastructure
│   ├── docker-compose.langfuse.yml  # Langfuse self-hosted (6 containers)
│   ├── langfuse.service             # systemd unit
│   ├── <agent-name>.service         # systemd unit
│   └── setup.sh                     # One-shot install script
├── src/
│   ├── main.py                 # Entry point: Web + Bot + Skill loading
│   ├── config.py               # Config parser + LLM factory
│   ├── skills/                 # Skill loader (tools + domain)
│   │   └── __init__.py         # load_tool_skills() + load_domain_skill()
│   ├── agent/
│   │   ├── graph.py            # LangGraph StateGraph + SqliteSaver
│   │   ├── nodes.py            # Node logic (with skill-loading node)
│   │   └── state.py            # TypedDict state
│   ├── tools/
│   │   └── __init__.py         # Domain-specific tools
│   ├── web/
│   │   ├── app.py              # FastAPI + SSE streaming + replay API
│   │   └── templates/
│   │       └── index.html
│   └── bot/
│       └── telegram.py         # python-telegram-bot handler
└── tests/
    └── test_agent.py
```

**Then deploy:**
```bash
uv sync
bash infra/setup.sh
# Web UI: http://0.0.0.0:8080
# Langfuse: http://localhost:3000
# Telegram Bot: running
# Survives reboot: ✅
```

<br>

## 🎯 Key Highlights

<table>
<tr>
<td width="33%">

### 🔌 Multi-LLM Hot-Swap
Switch AI providers with one config line. Zero code changes.

```toml
[llm]
provider = "deepseek"  # ← just change this
# provider = "anthropic"
# provider = "openai"
model = "deepseek-v4-pro"
```

</td>
<td width="33%">

### 🧠 Dual Skill System
Toolbox + Knowledge base. Distilled from Anthropic's financial AI patterns.

```python
# Tool skills (Python modules)
tools = load_tool_skills(["web-search", "data-analysis"])

# Domain skills (.md knowledge base)
context = load_skill_for_intent("analyze")
```

</td>
<td width="33%">

### 🏗️ Production Deploy
systemd-managed processes with auto-restart on crash.

```bash
bash infra/setup.sh
systemctl --user status my-agent
journalctl --user -u my-agent -f
```

</td>
</tr>
</table>

<br>

## 🎨 Two Modes

### ⚡ Scaffold Mode
> "Build me a customer support bot with web UI and Langfuse"

Straight to production. 30 seconds.

### 🧙 Wizard Mode
> "I want to build an AI agent but not sure how..."

Step-by-step guidance: Agent type → LLM provider → Interface → Observability → Persistence → Tools. Recommendations at every step.

<br>

## 🧩 Skills Marketplace

5 pre-built tool skills ship with Agent Builder. Copy into your project and go:

| Skill | Tools | Requires |
|-------|-------|----------|
| **web-search** | `search_web`, `fetch_page` | Tavily API |
| **file-system** | `read_file`, `write_file`, `list_dir` | None |
| **data-analysis** | `analyze_csv`, `create_chart` | pandas, plotly |
| **code-interpreter** | `run_python`, `install_package` | None |
| **financial-data** | `get_spot`, `get_financials`, `get_option_chain`, `get_etf_holdings` | akshare |

Plus 3 domain skill templates (`skills/domain-basics.md`, `strategies.md`, `risk-management.md`) — the agent auto-loads them based on user intent. This is the core pattern from Anthropic's financial-services repo.

<br>

## 📦 Infrastructure

```
┌─────────────────────────────────┐
│ systemd --user                   │
│  ┌─ langfuse.service ──────────┐ │
│  │  docker compose up -d        │ │
│  │  ├─ postgres                 │ │
│  │  ├─ clickhouse               │ │
│  │  ├─ redis                    │ │
│  │  ├─ minio                    │ │
│  │  ├─ langfuse-web (:3000)     │ │
│  │  └─ langfuse-worker          │ │
│  └─────────────────────────────┘ │
│           │ depends on            │
│           ▼                       │
│  ┌─ agent.service ─────────────┐ │
│  │  python -m src.main          │ │
│  │  ├─ FastAPI (:8080)          │ │
│  │  └─ Telegram Bot (polling)   │ │
│  └─────────────────────────────┘ │
└─────────────────────────────────┘
```

```bash
# Deploy
bash infra/setup.sh

# Day-to-day
systemctl --user status my-agent
journalctl --user -u my-agent -f
systemctl --user restart my-agent

# Keep alive after SSH disconnect
sudo loginctl enable-linger $USER
```

<br>

## 📚 Reference Docs

| Document | Content |
|----------|---------|
| [`SKILL.md`](SKILL.md) | Core skill definition — complete scaffold workflow |
| [`references/llm-config.md`](references/llm-config.md) | Multi-LLM configuration spec |
| [`references/langgraph-patterns.md`](references/langgraph-patterns.md) | LangGraph basics: state, routing, checkpoints |
| [`references/langgraph-patterns-deep.md`](references/langgraph-patterns-deep.md) | LangGraph advanced: streaming, HITL, error handling |
| [`references/langfuse-setup.md`](references/langfuse-setup.md) | Langfuse integration: cloud/self-hosted, attributes, scoring |
| [`references/tool-patterns.md`](references/tool-patterns.md) | 4 tool patterns: API wrappers, file system, MCP, database |
| [`references/infrastructure.md`](references/infrastructure.md) | systemd + Docker Compose deployment guide |
| [`references/financial-tools.md`](references/financial-tools.md) | AKShare financial data integration |
| [`references/financial-services-patterns.md`](references/financial-services-patterns.md) | Anthropic financial AI architecture analysis |

<br>

## 🔧 Tech Stack

| Technology | Role |
|------------|------|
| **LangGraph 1.x** | Agent state graph engine |
| **LangChain** | LLM abstraction + tool binding |
| **FastAPI** | Web API + SSE streaming |
| **HTMX** | Frontend interactivity (no heavy JS) |
| **python-telegram-bot** | Telegram Bot interface |
| **Langfuse** | LLM observability (cloud + self-hosted) |
| **systemd** | Process supervision, auto-restart, boot-start |
| **Docker Compose** | Langfuse self-hosted stack |
| **uv** | Python package manager |
| **Docker** | Containerized deployment |

<br>

## 🤔 FAQ

<details>
<summary><b>Q: 这和直接用 LangGraph 有什么区别？ / How is this different from raw LangGraph?</b></summary>

纯 LangGraph 给你画布和颜料。Agent Builder 给你一整套已经画好的、可以直接挂到墙上的作品——含 systemd 部署、Langfuse 追踪、Telegram + Web 双界面、还有一套可复用的 Skills 市场。

Raw LangGraph gives you canvas and paint. Agent Builder gives you a finished, framed piece ready to hang — with systemd deployment, Langfuse tracing, Telegram + Web interfaces, and a reusable Skills marketplace.

</details>

<details>
<summary><b>Q: Tool Skills 和 Domain Skills 有什么区别？ / What's the difference between Tool and Domain Skills?</b></summary>

**Tool Skills** 是可执行的 Python 代码——搜索网络、读取文件、分析数据。**Domain Skills** 是 .md 知识文件——教 Agent 怎么思考。前者是手，后者是脑。两个系统来自 Anthropic financial-services 项目的生产实践。

Tool Skills are executable Python code — search the web, read files, analyze data. Domain Skills are .md knowledge files — they teach the agent HOW to think. Hands vs. brain. Both patterns are from Anthropic's production financial-services repo.

</details>

<details>
<summary><b>Q: 生成的代码质量怎么样？ / What's the code quality like?</b></summary>

看起来像是你团队里最资深的工程师写的。类型安全、异步优先、错误处理完善、配置分离、systemd 部署——这些都是标配。

Looks like your most senior engineer wrote it. Type-safe, async-first, proper error handling, config separation, systemd deployment — all standard.

</details>

<details>
<summary><b>Q: 我能改生成的代码吗？ / Can I modify the generated code?</b></summary>

当然。这就是你的项目。生成只是起点——你想怎么改都行。当然，下次你再用 Agent Builder 生成东西的时候，它不会记得你的改动（除非你告诉它）。

Of course. It's your project. Generation is just the starting point — modify everything. Though Agent Builder won't remember your changes next time you generate (unless you tell it to).

</details>

<details>
<summary><b>Q: 支持哪些 LLM？ / Which LLMs are supported?</b></summary>

DeepSeek ✓ · Anthropic (Claude) ✓ · OpenAI (GPT) ✓ · 任何 OpenAI 兼容接口 ✓  
在 `config.toml` 里改一行就行。 / One line in `config.toml`.

</details>

<br>

---

<br>

<div align="center">

<h3>Made with 🏗️ Agent Builder — by an agent, for builders</h3>
<p><em>This Claude Code skill generates production AI agents.<br>Now it's yours. Share it. Ship it. Build something.</em></p>

<br>

<img src="https://img.shields.io/badge/Made%20with-Python-3776AB?style=flat-square&logo=python">
<img src="https://img.shields.io/badge/Powered%20by-LangGraph-1C3C3C?style=flat-square&logo=langchain">
<img src="https://img.shields.io/badge/Runs%20on-Claude%20Code-E68B2C?style=flat-square">
<img src="https://img.shields.io/badge/Deploys%20with-systemd-E95420?style=flat-square&logo=linux">

<br><br>

> ⚠️ **Disclaimer / 免责声明**：本项目纯属个人业余兴趣爱好，与本人任职公司无关。This is a personal hobby project, not affiliated with or endorsed by my employer.

</div>

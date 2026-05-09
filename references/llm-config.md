# LLM Configuration

## config.toml Format

```toml
[llm]
provider = "deepseek"        # deepseek | anthropic | openai | custom
api_key = "${LLM_API_KEY}"   # env var expansion
model = "deepseek-v4-pro"
base_url = "https://api.deepseek.com/v1"  # optional, for custom providers
temperature = 0.7
max_tokens = 4096

# Alternative: Anthropic
# [llm]
# provider = "anthropic"
# api_key = "${ANTHROPIC_API_KEY}"
# model = "claude-sonnet-4-6"

# Alternative: OpenAI
# [llm]
# provider = "openai"
# api_key = "${OPENAI_API_KEY}"
# model = "gpt-4o"

# Alternative: Any OpenAI-compatible
# [llm]
# provider = "openai"
# api_key = "${CUSTOM_API_KEY}"
# model = "custom-model"
# base_url = "https://your-api.com/v1"
```

## Python Factory

```python
import os
import tomllib
from dataclasses import dataclass
from langchain_core.language_models import BaseChatModel
from langchain_deepseek import ChatDeepSeek
from langchain_anthropic import ChatAnthropic
from langchain_openai import ChatOpenAI


@dataclass
class LLMConfig:
    provider: str
    api_key: str
    model: str
    base_url: str | None = None
    temperature: float = 0.7
    max_tokens: int = 4096

    @classmethod
    def from_toml(cls, path: str = "config.toml") -> "LLMConfig":
        with open(path, "rb") as f:
            data = tomllib.load(f)
        llm = data["llm"]
        return cls(
            provider=llm["provider"],
            api_key=os.path.expandvars(llm["api_key"]),
            model=llm["model"],
            base_url=llm.get("base_url"),
            temperature=llm.get("temperature", 0.7),
            max_tokens=llm.get("max_tokens", 4096),
        )


def build_llm(cfg: LLMConfig) -> BaseChatModel:
    match cfg.provider:
        case "deepseek":
            return ChatDeepSeek(
                model=cfg.model,
                api_key=cfg.api_key,
                temperature=cfg.temperature,
                max_tokens=cfg.max_tokens,
            )
        case "anthropic":
            return ChatAnthropic(
                model=cfg.model,
                api_key=cfg.api_key,
                temperature=cfg.temperature,
                max_tokens=cfg.max_tokens,
            )
        case "openai":
            return ChatOpenAI(
                model=cfg.model,
                api_key=cfg.api_key,
                base_url=cfg.base_url,
                temperature=cfg.temperature,
                max_tokens=cfg.max_tokens,
            )
        case _:
            raise ValueError(f"Unknown LLM provider: {cfg.provider}")
```

## .env.example

Always include this file listing all required env vars:

```
LLM_API_KEY=sk-...
LANGFUSE_PUBLIC_KEY=pk-...
LANGFUSE_SECRET_KEY=sk-...
TELEGRAM_BOT_TOKEN=...
```

## Dependencies (pyproject.toml)

```toml
[project]
dependencies = [
    "langgraph>=0.2.0",
    "langchain-deepseek>=0.1.0",
    "langchain-anthropic>=0.2.0",
    "langchain-openai>=0.2.0",
    "langfuse>=2.0.0",
    "python-telegram-bot>=21.0",
    "fastapi>=0.115.0",
    "uvicorn[standard]>=0.30.0",
    "jinja2>=3.1.0",
    "httpx>=0.27.0",
]
```

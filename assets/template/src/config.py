import os
import tomllib
from dataclasses import dataclass
from langchain_core.language_models import BaseChatModel


@dataclass
class LLMConfig:
    provider: str
    api_key: str
    model: str
    base_url: str | None = None
    temperature: float = 0.7
    max_tokens: int = 4096


@dataclass
class LangfuseConfig:
    public_key: str
    secret_key: str
    host: str = "https://cloud.langfuse.com"


@dataclass
class TelegramConfig:
    bot_token: str


@dataclass
class WebConfig:
    host: str = "0.0.0.0"
    port: int = 8080


@dataclass
class AgentConfig:
    checkpoint_db: str = "data/checkpoints.db"
    max_history: int = 50


@dataclass
class SkillsConfig:
    enabled: list[str] = None

    def __post_init__(self):
        if self.enabled is None:
            self.enabled = []


@dataclass
class Config:
    llm: LLMConfig
    langfuse: LangfuseConfig
    telegram: TelegramConfig
    web: WebConfig
    agent: AgentConfig
    skills: SkillsConfig

    @classmethod
    def from_toml(cls, path: str = "config.toml") -> "Config":
        with open(path, "rb") as f:
            data = tomllib.load(f)

        llm = data["llm"]
        langfuse = data["langfuse"]
        telegram = data["telegram"]
        web = data.get("web", {})
        agent = data.get("agent", {})
        skills = data.get("skills", {})

        return cls(
            llm=LLMConfig(
                provider=llm["provider"],
                api_key=os.path.expandvars(llm["api_key"]),
                model=llm["model"],
                base_url=llm.get("base_url"),
                temperature=llm.get("temperature", 0.7),
                max_tokens=llm.get("max_tokens", 4096),
            ),
            langfuse=LangfuseConfig(
                public_key=os.path.expandvars(langfuse["public_key"]),
                secret_key=os.path.expandvars(langfuse["secret_key"]),
                host=langfuse.get("host", "https://cloud.langfuse.com"),
            ),
            telegram=TelegramConfig(
                bot_token=os.path.expandvars(telegram["bot_token"]),
            ),
            web=WebConfig(
                host=web.get("host", "0.0.0.0"),
                port=web.get("port", 8080),
            ),
            agent=AgentConfig(
                checkpoint_db=agent.get("checkpoint_db", "data/checkpoints.db"),
                max_history=agent.get("max_history", 50),
            ),
            skills=SkillsConfig(
                enabled=skills.get("enabled", []),
            ),
        )


def build_llm(cfg: LLMConfig) -> BaseChatModel:
    if cfg.provider == "deepseek":
        from langchain_deepseek import ChatDeepSeek
        return ChatDeepSeek(
            model=cfg.model,
            api_key=cfg.api_key,
            temperature=cfg.temperature,
            max_tokens=cfg.max_tokens,
        )
    elif cfg.provider == "anthropic":
        from langchain_anthropic import ChatAnthropic
        return ChatAnthropic(
            model=cfg.model,
            api_key=cfg.api_key,
            temperature=cfg.temperature,
            max_tokens=cfg.max_tokens,
        )
    elif cfg.provider == "openai":
        from langchain_openai import ChatOpenAI
        return ChatOpenAI(
            model=cfg.model,
            api_key=cfg.api_key,
            base_url=cfg.base_url,
            temperature=cfg.temperature,
            max_tokens=cfg.max_tokens,
        )
    else:
        raise ValueError(f"Unknown LLM provider: {cfg.provider}")

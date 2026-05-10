import os
import tomllib
from dataclasses import dataclass, field
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
class InterfacesConfig:
    enabled: list[str] = field(default_factory=lambda: ["web", "telegram"])
    web: dict = field(default_factory=lambda: {"host": "0.0.0.0", "port": 8080})
    telegram: dict = field(default_factory=dict)

    @classmethod
    def from_dict(cls, data: dict) -> "InterfacesConfig":
        return cls(
            enabled=data.get("enabled", ["web", "telegram"]),
            web=data.get("web", {}),
            telegram=data.get("telegram", {}),
        )


@dataclass
class AgentConfig:
    checkpoint_db: str = "data/checkpoints.db"
    max_history: int = 50


@dataclass
class SkillsConfig:
    enabled: list[str] = field(default_factory=list)
    config: dict[str, dict] = field(default_factory=dict)

    @classmethod
    def from_dict(cls, data: dict) -> "SkillsConfig":
        return cls(
            enabled=data.get("enabled", []),
            config=data.get("config", {}),
        )

    def get_skill_config(self, skill_name: str) -> dict:
        """Return user config for a skill, or empty dict if not set."""
        return self.config.get(skill_name, {})


@dataclass
class Config:
    llm: LLMConfig
    langfuse: LangfuseConfig
    interfaces: InterfacesConfig
    agent: AgentConfig
    skills: SkillsConfig

    @classmethod
    def from_toml(cls, path: str = "config.toml") -> "Config":
        with open(path, "rb") as f:
            data = tomllib.load(f)

        llm = data["llm"]
        langfuse = data["langfuse"]
        interfaces = data.get("interfaces", {})
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
            interfaces=InterfacesConfig.from_dict(interfaces),
            agent=AgentConfig(
                checkpoint_db=agent.get("checkpoint_db", "data/checkpoints.db"),
                max_history=agent.get("max_history", 50),
            ),
            skills=SkillsConfig.from_dict(skills),
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

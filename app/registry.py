"""
Registry for Quality Autopilot AgentOS.

Provides shared tools and models for AgentOS.

All models route through the Kilo AI Gateway (OpenRouter-compatible).
Free models require no API key; paid tiers activate with KILO_API_KEY.
"""

from os import getenv

from agno.models.openrouter import OpenRouter
from agno.registry import Registry

from app.settings import MODEL, agent_db, get_parallel_tools

KILO_BASE_URL = getenv("OPENROUTER_BASE_URL", "https://api.kilo.ai/api/openrouter/v1")


def _kilo(model_id: str) -> OpenRouter:
    """Create an OpenRouter model instance routed through Kilo Gateway."""
    api_key = getenv("OPENROUTER_API_KEY", "anonymous")
    return OpenRouter(id=model_id, base_url=KILO_BASE_URL, api_key=api_key)


# Monkey-patch OpenRouter to ensure dynamically loaded agents use Kilo Gateway
_original_get_client_params = OpenRouter._get_client_params


def _patched_get_client_params(self) -> dict:  # type: ignore[override]
    if not self.base_url or self.base_url == "https://openrouter.ai/api/v1":
        self.base_url = KILO_BASE_URL
    if not self.api_key or self.api_key == "not-provided":
        self.api_key = getenv("OPENROUTER_API_KEY", "anonymous")
    return _original_get_client_params(self)


OpenRouter._get_client_params = _patched_get_client_params


# ---------------------------------------------------------------------------
# Models
# ---------------------------------------------------------------------------
def _get_models() -> list:  # type: ignore[type-arg]
    """Build the model list — all routed through Kilo AI Gateway."""

    # -- Core: default model from settings (kilo-auto/free) -----------------
    models: list = [MODEL]

    # -- Kilo Auto virtual tiers (always available) -------------------------
    models.extend(
        [
            _kilo("kilo-auto/free"),
            _kilo("kilo-auto/small"),
        ]
    )

    # -- Paid tiers (available when a Kilo API key is configured) -----------
    kilo_key = getenv("KILO_API_KEY", "anonymous")
    if kilo_key and kilo_key != "anonymous":
        models.extend(
            [
                _kilo("kilo-auto/balanced"),
                _kilo("kilo-auto/frontier"),
                _kilo("anthropic/claude-sonnet-4.6"),
                _kilo("anthropic/claude-haiku-4.5"),
                _kilo("openai/gpt-5.4"),
                _kilo("openai/gpt-5.4-mini"),
                _kilo("google/gemini-2.5-flash"),
                _kilo("x-ai/grok-4"),
                _kilo("deepseek/deepseek-v3.2"),
            ]
        )

    return models


# ---------------------------------------------------------------------------
# Tools
# ---------------------------------------------------------------------------
def _get_tools() -> list:  # type: ignore[type-arg]
    """Build the tool list, gating optional tools on API keys or packages."""
    from agno.tools.calculator import CalculatorTools
    from agno.tools.coding import CodingTools
    from agno.tools.file import FileTools
    from agno.tools.file_generation import FileGenerationTools
    from agno.tools.reasoning import ReasoningTools

    tools: list = [
        *get_parallel_tools(),
        CalculatorTools(),
        FileTools(),
        FileGenerationTools(),
        CodingTools(),
        ReasoningTools(add_instructions=True),
    ]

    # Free search — needs ddgs package
    try:
        from agno.tools.duckduckgo import DuckDuckGoTools

        tools.append(DuckDuckGoTools())
    except ImportError:
        pass

    # Knowledge enrichment — needs wikipedia package
    try:
        from agno.tools.wikipedia import WikipediaTools

        tools.append(WikipediaTools())
    except ImportError:
        pass

    # --- Env-gated tools ---------------------------------------------------

    if getenv("GITHUB_TOKEN") or getenv("GITHUB_ACCESS_TOKEN"):
        from agno.tools.github import GithubTools

        tools.append(
            GithubTools(
                access_token=getenv("GITHUB_TOKEN") or getenv("GITHUB_ACCESS_TOKEN")
            )
        )

    if getenv("EXA_API_KEY"):
        from agno.tools.exa import ExaTools

        tools.append(ExaTools())

    if getenv("JIRA_API_TOKEN"):
        try:
            from agno.tools.jira import JiraTools

            tools.append(
                JiraTools(
                    server_url=getenv("JIRA_URL", ""),
                    username=getenv("JIRA_USERNAME", ""),
                    token=getenv("JIRA_API_TOKEN", ""),
                )
            )
        except (ImportError, Exception):
            pass

    return tools


# ---------------------------------------------------------------------------
# Registry
# ---------------------------------------------------------------------------
registry = Registry(
    tools=_get_tools(),
    models=_get_models(),
    dbs=[agent_db],
)

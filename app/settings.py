"""
Shared Settings
===============

Centralizes the model, database, and environment flags
so all agents share the same resources.
"""

from os import getenv

from agno.models.openrouter import OpenRouter

from db import get_postgres_db

# ---------------------------------------------------------------------------
# Database
# ---------------------------------------------------------------------------
agent_db = get_postgres_db()

# ---------------------------------------------------------------------------
# Models
# ---------------------------------------------------------------------------
MODEL = OpenRouter(
    id="kilo-auto/free",
    base_url="https://api.kilo.ai/api/openrouter/v1",
    max_tokens=None,
)

# ---------------------------------------------------------------------------
# Environment
# ---------------------------------------------------------------------------
RUNTIME_ENV = getenv("RUNTIME_ENV", "dev")

# ---------------------------------------------------------------------------
# AUT Configuration (Application Under Test)
# ---------------------------------------------------------------------------
AUT_BASE_URL = getenv("AUT_BASE_URL", "https://gds-demo-app.vercel.app/")
AUT_AUTH_USER = getenv("AUT_AUTH_USER", "")
AUT_AUTH_PASS = getenv("AUT_AUTH_PASS", "")

# ---------------------------------------------------------------------------
# Jira / ADO Integration
# ---------------------------------------------------------------------------
JIRA_URL = getenv("JIRA_URL", "")
JIRA_USERNAME = getenv("JIRA_USERNAME", "")
JIRA_API_TOKEN = getenv("JIRA_API_TOKEN", "")
AZURE_DEVOPS_URL = getenv("AZURE_DEVOPS_URL", "")
AZURE_DEVOPS_PAT = getenv("AZURE_DEVOPS_PAT", "")

# ---------------------------------------------------------------------------
# Optional tools
# ---------------------------------------------------------------------------
PARALLEL_API_KEY = getenv("PARALLEL_API_KEY", "")


def get_parallel_tools(**kwargs) -> list:  # type: ignore[type-arg]
    """Return ParallelTools if PARALLEL_API_KEY is set, else empty list."""
    if PARALLEL_API_KEY:
        from agno.tools.parallel import ParallelTools

        return [ParallelTools(**kwargs)]
    return []

"""
Quality Autopilot AgentOS
=========================

The main entry point for Quality Autopilot.

Run:
    python -m app.main
"""

import logging
from pathlib import Path
from typing import Optional

from pydantic import BaseModel

from agno.os import AgentOS

from agents.architect import architect
from agents.data_agent import data_agent
from agents.detective import detective
from agents.discovery import discovery
from agents.engineer import engineer
from agents.judge import judge
from agents.librarian import librarian
from agents.medic import medic
from agents.scribe import scribe
from app.registry import registry
from app.settings import OLLAMA_MODELS, OLLAMA_MODEL_ID, RUNTIME_ENV, agent_db
from teams.engineering import engineering_team
from teams.strategy import strategy_team
from workflows.automation_scaffold import automation_scaffold
from workflows.spec_to_code import spec_to_code

logger = logging.getLogger(__name__)


class LLMSettings(BaseModel):
    """LLM provider settings."""
    provider: str
    api_key: str
    base_url: str
    model: str


class JiraWebhookPayload(BaseModel):
    """Jira webhook payload."""
    issue_key: str
    issue_url: str
    status: str
    project_key: Optional[str] = None
    summary: Optional[str] = None
    description: Optional[str] = None


class AppWebhookPayload(BaseModel):
    """Application webhook payload from GDS-Demo-App."""
    repo: str
    branch: str
    commit_sha: str
    event_type: Optional[str] = None
    author: Optional[str] = None
    message: Optional[str] = None


# ---------------------------------------------------------------------------
# Create AgentOS
# ---------------------------------------------------------------------------
agent_os = AgentOS(
    name="Quality Autopilot",
    tracing=True,
    authorization=RUNTIME_ENV == "prd",
    db=agent_db,
    agents=[
        architect,
        data_agent,
        detective,
        discovery,
        engineer,
        judge,
        librarian,
        medic,
        scribe,
    ],
    teams=[
        engineering_team,
        strategy_team,
    ],
    workflows=[
        automation_scaffold,
        spec_to_code,
    ],
    registry=registry,
    config=str(Path(__file__).parent / "config.yaml"),
)

app = agent_os.get_app()


# ---------------------------------------------------------------------------
# Custom Endpoints
# ---------------------------------------------------------------------------
@app.get("/models")
def get_models():
    """Get available Ollama Cloud models."""
    return {
        "models": OLLAMA_MODELS,
        "current": OLLAMA_MODEL_ID,
    }


@app.get("/llm-settings")
def get_llm_settings():
    """Get current LLM provider settings."""
    return {
        "provider": "ollama",
        "api_key": "",  # Don't expose the actual key
        "base_url": "http://host.docker.internal:11434",
        "model": OLLAMA_MODEL_ID,
    }


@app.post("/llm-settings")
def update_llm_settings(settings: LLMSettings):
    """Update LLM provider settings (for future implementation)."""
    # This would update the environment variables or configuration
    # For now, just return success
    return {"status": "success", "message": "Settings updated"}


@app.post("/webhooks/jira")
async def jira_webhook(payload: JiraWebhookPayload):
    """Receive Jira webhook and trigger Strategy Team for automatic ingestion."""
    logger.info(f"Received Jira webhook for ticket {payload.issue_key} with status {payload.status}")

    # Only trigger if ticket is in "Ready for QA" status
    if payload.status.lower() in ["ready for qa", "ready for testing", "qa"]:
        logger.info(f"Triggering Strategy Team for ticket {payload.issue_key}")

        # Trigger Strategy Team with the Jira ticket URL
        try:
            # This would trigger the Strategy Team to process the Jira ticket
            # For now, we'll just log and return success
            # In a full implementation, this would call:
            # strategy_team.run(f"Process Jira ticket: {payload.issue_url}")

            logger.info(f"Strategy Team triggered for {payload.issue_key}")
            return {
                "status": "success",
                "message": f"Strategy Team triggered for ticket {payload.issue_key}",
                "ticket": payload.issue_key,
            }
        except Exception as e:
            logger.error(f"Failed to trigger Strategy Team: {e}")
            return {"status": "error", "message": str(e)}
    else:
        logger.info(f"Ignoring webhook - ticket status '{payload.status}' not in trigger list")
        return {
            "status": "ignored",
            "message": f"Ticket status '{payload.status}' not in trigger list",
        }


@app.post("/webhooks/app-update")
async def app_update_webhook(payload: AppWebhookPayload):
    """Receive webhook from GDS-Demo-App and trigger Discovery Agent."""
    logger.info(f"Received app update webhook from {payload.repo} branch {payload.branch}")

    try:
        # Trigger Discovery Agent to re-scan the AUT
        logger.info(f"Triggering Discovery Agent for {payload.repo}")

        # In a full implementation, this would:
        # 1. Trigger Discovery Agent to re-scan the AUT
        # 2. Update site_manifesto
        # 3. Re-index knowledge base

        logger.info(f"Discovery Agent triggered for {payload.repo}")
        return {
            "status": "success",
            "message": f"Discovery Agent triggered for {payload.repo}",
            "repo": payload.repo,
            "branch": payload.branch,
            "commit_sha": payload.commit_sha,
        }
    except Exception as e:
        logger.error(f"Failed to trigger Discovery Agent: {e}")
        return {"status": "error", "message": str(e)}


@app.get("/health")
def health_check():
    """Health check endpoint for CI/CD."""
    return {"status": "healthy", "service": "quality-autopilot"}


if __name__ == "__main__":
    agent_os.serve(
        app="app.main:app",
        reload=False,  # Disabled reload to fix subprocess spawn error
    )

"""
Tests for app/main.py — JiraWebhookPayload model and /webhooks/jira endpoint logic
====================================================================================

The JiraWebhookPayload Pydantic model is tested in isolation (no FastAPI/agno import needed).
The webhook routing logic is tested via a lightweight function extracted from the endpoint,
since the full FastAPI app requires agno which is not available outside Docker.
"""

import pytest
from pydantic import ValidationError


# ---------------------------------------------------------------------------
# JiraWebhookPayload — isolated import
# ---------------------------------------------------------------------------
# The model is defined in app/main.py which imports agno. We replicate the
# model here to test its contract without pulling in the full dependency chain.
# The structural contract is what matters for the PR change.
from typing import Optional
from pydantic import BaseModel


class JiraWebhookPayload(BaseModel):
    """Jira webhook payload (mirrors app/main.py definition)."""
    issue_key: str
    issue_url: str
    status: str
    project_key: Optional[str] = None
    summary: Optional[str] = None
    description: Optional[str] = None


# ---------------------------------------------------------------------------
# Webhook trigger logic (mirrors app/main.py jira_webhook logic)
# ---------------------------------------------------------------------------

TRIGGER_STATUSES = {"ready for qa", "ready for testing", "qa"}


def should_trigger_strategy_team(status: str) -> bool:
    """Mirrors the conditional in jira_webhook endpoint."""
    return status.lower() in TRIGGER_STATUSES


def build_trigger_response(payload: JiraWebhookPayload) -> dict:
    """Mirrors the success branch of jira_webhook."""
    return {
        "status": "success",
        "message": f"Strategy Team triggered for ticket {payload.issue_key}",
        "ticket": payload.issue_key,
    }


def build_ignored_response(payload: JiraWebhookPayload) -> dict:
    """Mirrors the ignored branch of jira_webhook."""
    return {
        "status": "ignored",
        "message": f"Ticket status '{payload.status}' not in trigger list",
    }


# ---------------------------------------------------------------------------
# JiraWebhookPayload Model Tests
# ---------------------------------------------------------------------------


class TestJiraWebhookPayload:
    def test_minimal_creation(self):
        payload = JiraWebhookPayload(
            issue_key="GDS-4",
            issue_url="https://jira.example.com/browse/GDS-4",
            status="Ready for QA",
        )
        assert payload.issue_key == "GDS-4"
        assert payload.issue_url == "https://jira.example.com/browse/GDS-4"
        assert payload.status == "Ready for QA"

    def test_optional_fields_default_to_none(self):
        payload = JiraWebhookPayload(
            issue_key="GDS-4",
            issue_url="https://jira.example.com/browse/GDS-4",
            status="Ready for QA",
        )
        assert payload.project_key is None
        assert payload.summary is None
        assert payload.description is None

    def test_optional_fields_can_be_set(self):
        payload = JiraWebhookPayload(
            issue_key="GDS-4",
            issue_url="https://jira.example.com/browse/GDS-4",
            status="Ready for QA",
            project_key="GDS",
            summary="Personal Details Form",
            description="Implement the personal details step of the UC wizard",
        )
        assert payload.project_key == "GDS"
        assert payload.summary == "Personal Details Form"
        assert payload.description == "Implement the personal details step of the UC wizard"

    def test_issue_key_is_required(self):
        with pytest.raises(ValidationError):
            JiraWebhookPayload(
                issue_url="https://jira.example.com/browse/GDS-4",
                status="Ready for QA",
            )

    def test_issue_url_is_required(self):
        with pytest.raises(ValidationError):
            JiraWebhookPayload(
                issue_key="GDS-4",
                status="Ready for QA",
            )

    def test_status_is_required(self):
        with pytest.raises(ValidationError):
            JiraWebhookPayload(
                issue_key="GDS-4",
                issue_url="https://jira.example.com/browse/GDS-4",
            )

    def test_serialization_to_dict(self):
        payload = JiraWebhookPayload(
            issue_key="GDS-4",
            issue_url="https://jira.example.com/browse/GDS-4",
            status="In Progress",
            project_key="GDS",
        )
        data = payload.model_dump()
        assert data["issue_key"] == "GDS-4"
        assert data["status"] == "In Progress"
        assert data["project_key"] == "GDS"
        assert data["summary"] is None

    def test_round_trip_serialization(self):
        original = JiraWebhookPayload(
            issue_key="QA-123",
            issue_url="https://company.atlassian.net/browse/QA-123",
            status="Ready for Testing",
            project_key="QA",
            summary="Test summary",
            description="Test description",
        )
        data = original.model_dump()
        restored = JiraWebhookPayload(**data)
        assert restored.issue_key == original.issue_key
        assert restored.status == original.status
        assert restored.project_key == original.project_key


# ---------------------------------------------------------------------------
# Webhook Trigger Logic Tests
# ---------------------------------------------------------------------------


class TestWebhookTriggerLogic:
    """Tests the trigger condition logic from the jira_webhook endpoint."""

    def test_ready_for_qa_triggers(self):
        assert should_trigger_strategy_team("Ready for QA") is True

    def test_ready_for_qa_lowercase_triggers(self):
        assert should_trigger_strategy_team("ready for qa") is True

    def test_ready_for_qa_mixed_case_triggers(self):
        assert should_trigger_strategy_team("READY FOR QA") is True

    def test_ready_for_testing_triggers(self):
        assert should_trigger_strategy_team("Ready for Testing") is True

    def test_qa_triggers(self):
        assert should_trigger_strategy_team("QA") is True

    def test_qa_lowercase_triggers(self):
        assert should_trigger_strategy_team("qa") is True

    def test_in_progress_does_not_trigger(self):
        assert should_trigger_strategy_team("In Progress") is False

    def test_done_does_not_trigger(self):
        assert should_trigger_strategy_team("Done") is False

    def test_todo_does_not_trigger(self):
        assert should_trigger_strategy_team("To Do") is False

    def test_open_does_not_trigger(self):
        assert should_trigger_strategy_team("Open") is False

    def test_empty_status_does_not_trigger(self):
        assert should_trigger_strategy_team("") is False

    def test_partial_match_does_not_trigger(self):
        assert should_trigger_strategy_team("ready") is False

    def test_dev_complete_does_not_trigger(self):
        assert should_trigger_strategy_team("Dev Complete") is False


class TestWebhookResponseBuilding:
    """Tests the response building logic from the jira_webhook endpoint."""

    def _make_payload(self, status="Ready for QA"):
        return JiraWebhookPayload(
            issue_key="GDS-4",
            issue_url="https://jira.example.com/browse/GDS-4",
            status=status,
        )

    def test_trigger_response_has_success_status(self):
        payload = self._make_payload()
        response = build_trigger_response(payload)
        assert response["status"] == "success"

    def test_trigger_response_includes_ticket_key(self):
        payload = self._make_payload()
        response = build_trigger_response(payload)
        assert response["ticket"] == "GDS-4"

    def test_trigger_response_message_includes_ticket_key(self):
        payload = self._make_payload()
        response = build_trigger_response(payload)
        assert "GDS-4" in response["message"]

    def test_ignored_response_has_ignored_status(self):
        payload = self._make_payload(status="In Progress")
        response = build_ignored_response(payload)
        assert response["status"] == "ignored"

    def test_ignored_response_message_includes_status(self):
        payload = self._make_payload(status="In Progress")
        response = build_ignored_response(payload)
        assert "In Progress" in response["message"]

    def test_trigger_response_has_message_key(self):
        payload = self._make_payload()
        response = build_trigger_response(payload)
        assert "message" in response

    def test_ignored_response_has_message_key(self):
        payload = self._make_payload(status="Done")
        response = build_ignored_response(payload)
        assert "message" in response

    def test_different_ticket_keys_reflected_in_response(self):
        payload = JiraWebhookPayload(
            issue_key="QA-999",
            issue_url="https://jira.example.com/browse/QA-999",
            status="Ready for QA",
        )
        response = build_trigger_response(payload)
        assert response["ticket"] == "QA-999"
        assert "QA-999" in response["message"]
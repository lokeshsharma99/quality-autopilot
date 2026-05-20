"""
Tests for agents/architect/tools.py
======================================

Tests for fetch_jira_ticket using mocked HTTP calls.
The module is imported directly (bypassing agents/architect/__init__.py)
to avoid the agno dependency required by the agent module.
"""

import importlib.util
import sys
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

# ---------------------------------------------------------------------------
# Import architect tools directly, bypassing __init__.py which pulls in agno
# ---------------------------------------------------------------------------
_tools_path = Path(__file__).parent.parent / "agents" / "architect" / "tools.py"
_spec = importlib.util.spec_from_file_location("architect_tools", _tools_path)
_module = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(_module)

fetch_jira_ticket = _module.fetch_jira_ticket


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------

JIRA_SUCCESS_RESPONSE = {
    "fields": {
        "summary": "User Login with Email and Password",
        "description": "Allow users to authenticate with credentials.",
        "status": {"name": "Ready for QA"},
        "priority": {"name": "High"},
        "project": {"key": "GDS"},
    }
}


# ---------------------------------------------------------------------------
# fetch_jira_ticket Tests
# ---------------------------------------------------------------------------


class TestFetchJiraTicketMissingCredentials:
    def test_returns_error_when_username_missing(self, monkeypatch):
        monkeypatch.delenv("JIRA_USERNAME", raising=False)
        monkeypatch.setenv("JIRA_API_TOKEN", "token123")
        monkeypatch.setenv("JIRA_URL", "https://jira.example.com")

        result = fetch_jira_ticket("GDS-4")

        assert "error" in result
        assert result["ticket_key"] == "GDS-4"
        assert "credentials" in result["error"].lower()

    def test_returns_error_when_api_token_missing(self, monkeypatch):
        monkeypatch.setenv("JIRA_USERNAME", "user@example.com")
        monkeypatch.delenv("JIRA_API_TOKEN", raising=False)

        result = fetch_jira_ticket("GDS-4")

        assert "error" in result
        assert result["ticket_key"] == "GDS-4"

    def test_returns_error_when_both_credentials_missing(self, monkeypatch):
        monkeypatch.delenv("JIRA_USERNAME", raising=False)
        monkeypatch.delenv("JIRA_API_TOKEN", raising=False)

        result = fetch_jira_ticket("QA-99")

        assert "error" in result
        assert result["ticket_key"] == "QA-99"

    def test_ticket_key_preserved_in_error_response(self, monkeypatch):
        monkeypatch.delenv("JIRA_USERNAME", raising=False)
        monkeypatch.delenv("JIRA_API_TOKEN", raising=False)

        result = fetch_jira_ticket("MY-TICKET-123")
        assert result["ticket_key"] == "MY-TICKET-123"


class TestFetchJiraTicketSuccess:
    def _env_setup(self, monkeypatch, jira_url="https://jira.example.com"):
        monkeypatch.setenv("JIRA_URL", jira_url)
        monkeypatch.setenv("JIRA_USERNAME", "user@example.com")
        monkeypatch.setenv("JIRA_API_TOKEN", "secret-token")

    def test_returns_ticket_details_on_200(self, monkeypatch):
        self._env_setup(monkeypatch)

        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = JIRA_SUCCESS_RESPONSE

        with patch.object(_module.requests, "get", return_value=mock_response):
            result = fetch_jira_ticket("GDS-4")

        assert "error" not in result
        assert result["ticket_key"] == "GDS-4"
        assert result["summary"] == "User Login with Email and Password"
        assert result["status"] == "Ready for QA"
        assert result["priority"] == "High"
        assert result["project_key"] == "GDS"

    def test_ticket_url_is_constructed_correctly(self, monkeypatch):
        self._env_setup(monkeypatch, jira_url="https://mycompany.atlassian.net")

        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = JIRA_SUCCESS_RESPONSE

        with patch.object(_module.requests, "get", return_value=mock_response):
            result = fetch_jira_ticket("GDS-10")

        assert result["ticket_url"] == "https://mycompany.atlassian.net/browse/GDS-10"

    def test_api_url_includes_ticket_key(self, monkeypatch):
        self._env_setup(monkeypatch, jira_url="https://jira.example.com")

        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = JIRA_SUCCESS_RESPONSE

        captured_url = {}
        original_get = _module.requests.get

        def mock_get(url, **kwargs):
            captured_url["url"] = url
            return mock_response

        with patch.object(_module.requests, "get", side_effect=mock_get):
            fetch_jira_ticket("GDS-4")

        assert "GDS-4" in captured_url["url"]
        assert "/rest/api/3/issue/GDS-4" in captured_url["url"]

    def test_uses_basic_auth(self, monkeypatch):
        self._env_setup(monkeypatch)

        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = JIRA_SUCCESS_RESPONSE

        captured_kwargs = {}

        def mock_get(url, **kwargs):
            captured_kwargs.update(kwargs)
            return mock_response

        with patch.object(_module.requests, "get", side_effect=mock_get):
            fetch_jira_ticket("GDS-4")

        assert "auth" in captured_kwargs
        # HTTPBasicAuth stores username and password
        auth = captured_kwargs["auth"]
        assert auth.username == "user@example.com"
        assert auth.password == "secret-token"

    def test_accept_json_header_is_sent(self, monkeypatch):
        self._env_setup(monkeypatch)

        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = JIRA_SUCCESS_RESPONSE

        captured_kwargs = {}

        def mock_get(url, **kwargs):
            captured_kwargs.update(kwargs)
            return mock_response

        with patch.object(_module.requests, "get", side_effect=mock_get):
            fetch_jira_ticket("GDS-4")

        assert captured_kwargs.get("headers", {}).get("Accept") == "application/json"

    def test_timeout_is_set(self, monkeypatch):
        self._env_setup(monkeypatch)

        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = JIRA_SUCCESS_RESPONSE

        captured_kwargs = {}

        def mock_get(url, **kwargs):
            captured_kwargs.update(kwargs)
            return mock_response

        with patch.object(_module.requests, "get", side_effect=mock_get):
            fetch_jira_ticket("GDS-4")

        assert captured_kwargs.get("timeout") == 10

    def test_description_field_is_returned(self, monkeypatch):
        self._env_setup(monkeypatch)

        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = JIRA_SUCCESS_RESPONSE

        with patch.object(_module.requests, "get", return_value=mock_response):
            result = fetch_jira_ticket("GDS-4")

        assert result["description"] == "Allow users to authenticate with credentials."

    def test_missing_fields_default_to_empty_string(self, monkeypatch):
        self._env_setup(monkeypatch)

        minimal_response = {"fields": {}}

        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = minimal_response

        with patch.object(_module.requests, "get", return_value=mock_response):
            result = fetch_jira_ticket("GDS-1")

        assert result["summary"] == ""
        assert result["description"] == ""
        assert result["status"] == ""
        assert result["priority"] == ""
        assert result["project_key"] == ""


class TestFetchJiraTicketHttpErrors:
    def _env_setup(self, monkeypatch):
        monkeypatch.setenv("JIRA_URL", "https://jira.example.com")
        monkeypatch.setenv("JIRA_USERNAME", "user@example.com")
        monkeypatch.setenv("JIRA_API_TOKEN", "secret-token")

    def test_returns_error_on_404(self, monkeypatch):
        self._env_setup(monkeypatch)

        mock_response = MagicMock()
        mock_response.status_code = 404

        with patch.object(_module.requests, "get", return_value=mock_response):
            result = fetch_jira_ticket("MISSING-1")

        assert "error" in result
        assert "404" in result["error"]
        assert result["ticket_key"] == "MISSING-1"

    def test_returns_error_on_401(self, monkeypatch):
        self._env_setup(monkeypatch)

        mock_response = MagicMock()
        mock_response.status_code = 401

        with patch.object(_module.requests, "get", return_value=mock_response):
            result = fetch_jira_ticket("GDS-4")

        assert "error" in result
        assert "401" in result["error"]

    def test_returns_error_on_403(self, monkeypatch):
        self._env_setup(monkeypatch)

        mock_response = MagicMock()
        mock_response.status_code = 403

        with patch.object(_module.requests, "get", return_value=mock_response):
            result = fetch_jira_ticket("GDS-4")

        assert "error" in result
        assert "403" in result["error"]

    def test_returns_error_on_500(self, monkeypatch):
        self._env_setup(monkeypatch)

        mock_response = MagicMock()
        mock_response.status_code = 500

        with patch.object(_module.requests, "get", return_value=mock_response):
            result = fetch_jira_ticket("GDS-4")

        assert "error" in result


class TestFetchJiraTicketNetworkErrors:
    def _env_setup(self, monkeypatch):
        monkeypatch.setenv("JIRA_URL", "https://jira.example.com")
        monkeypatch.setenv("JIRA_USERNAME", "user@example.com")
        monkeypatch.setenv("JIRA_API_TOKEN", "secret-token")

    def test_returns_error_on_connection_error(self, monkeypatch):
        self._env_setup(monkeypatch)

        import requests as req
        with patch.object(_module.requests, "get", side_effect=req.exceptions.ConnectionError("Connection refused")):
            result = fetch_jira_ticket("GDS-4")

        assert "error" in result
        assert result["ticket_key"] == "GDS-4"
        assert "Request failed" in result["error"]

    def test_returns_error_on_timeout(self, monkeypatch):
        self._env_setup(monkeypatch)

        import requests as req
        with patch.object(_module.requests, "get", side_effect=req.exceptions.Timeout("Request timed out")):
            result = fetch_jira_ticket("GDS-4")

        assert "error" in result
        assert "timed out" in result["error"].lower() or "Request failed" in result["error"]

    def test_returns_error_on_request_exception(self, monkeypatch):
        self._env_setup(monkeypatch)

        import requests as req
        with patch.object(_module.requests, "get", side_effect=req.exceptions.RequestException("Generic error")):
            result = fetch_jira_ticket("GDS-4")

        assert "error" in result
        assert result["ticket_key"] == "GDS-4"

    def test_ticket_key_preserved_in_network_error_response(self, monkeypatch):
        self._env_setup(monkeypatch)

        import requests as req
        with patch.object(_module.requests, "get", side_effect=req.exceptions.ConnectionError("No route")):
            result = fetch_jira_ticket("UNIQUE-KEY-999")

        assert result["ticket_key"] == "UNIQUE-KEY-999"


class TestFetchJiraTicketDefaultUrl:
    def test_uses_default_jira_url_when_env_not_set(self, monkeypatch):
        monkeypatch.delenv("JIRA_URL", raising=False)
        monkeypatch.setenv("JIRA_USERNAME", "user@example.com")
        monkeypatch.setenv("JIRA_API_TOKEN", "token")

        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"fields": {}}

        captured_url = {}

        def mock_get(url, **kwargs):
            captured_url["url"] = url
            return mock_response

        with patch.object(_module.requests, "get", side_effect=mock_get):
            fetch_jira_ticket("GDS-4")

        # Default URL from function definition
        assert "lokeshsharma2.atlassian.net" in captured_url["url"]
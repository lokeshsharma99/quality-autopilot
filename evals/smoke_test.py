"""
Smoke Tests — Quality Autopilot
================================

Tests that every agent, team, and workflow can be imported and instantiated
without errors. These are Phase 0 gate tests — fast, no DB required.

Run:
    uv run python -m pytest evals/smoke_test.py -v
"""

import pytest


# ---------------------------------------------------------------------------
# Agent Import Tests
# ---------------------------------------------------------------------------
class TestAgentImports:
    def test_discovery_agent(self):
        from agents.discovery import discovery
        assert discovery.id == "discovery"

    def test_librarian_agent(self):
        from agents.librarian import librarian
        assert librarian.id == "librarian"

    def test_architect_agent(self):
        from agents.architect import architect
        assert architect.id == "architect"

    def test_scribe_agent(self):
        from agents.scribe import scribe
        assert scribe.id == "scribe"

    def test_judge_agent(self):
        from agents.judge import judge
        assert judge.id == "judge"

    def test_engineer_agent(self):
        from agents.engineer import engineer
        assert engineer.id == "engineer"

    def test_data_agent(self):
        from agents.data_agent import data_agent
        assert data_agent.id == "data-agent"

    def test_detective_agent(self):
        from agents.detective import detective
        assert detective.id == "detective"

    def test_medic_agent(self):
        from agents.medic import medic
        assert medic.id == "medic"


# ---------------------------------------------------------------------------
# Team Import Tests
# ---------------------------------------------------------------------------
class TestTeamImports:
    def test_context_team(self):
        from teams.context import context_team
        assert context_team.id == "context"

    def test_strategy_team(self):
        from teams.strategy import strategy_team
        assert strategy_team.id == "strategy"

    def test_engineering_team(self):
        from teams.engineering import engineering_team
        assert engineering_team.id == "engineering"

    def test_operations_team(self):
        from teams.operations import operations_team
        assert operations_team.id == "operations"


# ---------------------------------------------------------------------------
# Workflow Import Tests
# ---------------------------------------------------------------------------
class TestWorkflowImports:
    def test_discovery_onboard_workflow(self):
        from workflows.discovery_onboard import discovery_onboard
        assert discovery_onboard.id == "discovery-onboard"

    def test_spec_to_code_workflow(self):
        from workflows.spec_to_code import spec_to_code
        assert spec_to_code.id == "spec-to-code"

    def test_triage_heal_workflow(self):
        from workflows.triage_heal import triage_heal
        assert triage_heal.id == "triage-heal"


# ---------------------------------------------------------------------------
# Contract Validation Tests
# ---------------------------------------------------------------------------
class TestContracts:
    def test_site_manifesto(self):
        from contracts import SiteManifesto, PageEntry, UIComponent
        c = UIComponent(
            component_id="login-submit",
            component_type="button",
            data_testid="login-submit",
            accessibility_tree_hash="abc12345abcd1234",
        )
        p = PageEntry(
            page_id="login-page", url="http://localhost/login", route="/login",
            title="Login", page_type="login", is_auth_gated=False,
            components=[c], accessibility_tree_hash="abc12345abcd1234",
            crawled_at="2026-01-01T00:00:00",
        )
        m = SiteManifesto(
            manifesto_id="m-001", aut_base_url="http://localhost",
            aut_name="Test App", pages=[p],
            crawled_at="2026-01-01T00:00:00", crawl_duration_seconds=1.5,
        )
        assert m.aut_name == "Test App"
        assert len(m.pages) == 1

    def test_requirement_context(self):
        from contracts import AcceptanceCriterion, RequirementContext
        ac = AcceptanceCriterion(id="AC-001", description="User can log in", testable=True)
        r = RequirementContext(
            ticket_id="PROJ-001", title="Login", description="User login flow",
            acceptance_criteria=[ac], priority="P1", component="auth",
            source_url="http://jira/PROJ-001", affected_page_objects=["LoginPage"], is_new_feature=False,
        )
        assert r.ticket_id == "PROJ-001"
        assert len(r.acceptance_criteria) == 1

    def test_gherkin_spec(self):
        from contracts import DataRequirement, GherkinSpec
        dr = DataRequirement(field="email", type="string", constraints="unique email", pii_mask=True)
        g = GherkinSpec(
            ticket_id="PROJ-001",
            feature_file="features/login.feature",
            feature_content="Feature: Login\n  Scenario: Valid login\n    Given the user is on the login page",
            data_requirements=[dr],
            traceability={"AC-001": "Valid login"},
        )
        assert g.ticket_id == "PROJ-001"

    def test_judge_verdict(self):
        from contracts import JudgeVerdict
        v = JudgeVerdict(
            artifact_type="gherkin", agent_id="scribe", confidence=0.95, passed=True,
            checklist_results={"has_feature": True, "has_scenario": True},
            rejection_reasons=[], requires_human=False,
        )
        assert v.passed is True
        assert v.confidence >= 0.90

    def test_run_context(self):
        from contracts import RunContext, TestUser
        u = TestUser(username="qap_user_123", email="user.123@qap.test", password="QAP_Test_123!", role="user")
        rc = RunContext(
            ticket_id="PROJ-001", test_users=[u], db_seed_queries=[],
            api_mocks={}, cleanup_queries=[], pii_masked=True, unique_constraints_valid=True,
        )
        assert rc.pii_masked is True
        assert rc.test_users[0].email.endswith("@qap.test")

    def test_rca_report(self):
        from contracts import RCAReport
        r = RCAReport(
            test_name="login test", trace_id="t001", classification="LOCATOR_STALE",
            confidence=0.95, root_cause="Button testid changed",
            affected_file="automation/pages/login.page.ts",
            affected_locator="getByTestId('old-btn')",
            suggested_fix="Update to getByTestId('new-btn')",
            requires_human=False,
        )
        assert r.classification == "LOCATOR_STALE"
        assert r.requires_human is False

    def test_healing_patch(self):
        from contracts import HealingPatch
        p = HealingPatch(
            test_name="login test", trace_id="t001",
            file_path="automation/pages/login.page.ts",
            old_locator="getByTestId('old-btn')",
            new_locator="getByTestId('new-btn')",
            diff="--- a/login.page.ts\n+++ b/login.page.ts\n@@ -12 +12 @@\n-old\n+new",
            verification_passes=3, logic_changed=False,
        )
        assert p.verification_passes >= 3
        assert p.logic_changed is False


# ---------------------------------------------------------------------------
# Tool Unit Tests
# ---------------------------------------------------------------------------
class TestDetectiveTools:
    def test_parse_ci_log(self):
        from agents.detective.tools import parse_ci_log, classify_failure
        log = "ERROR: locator 'getByTestId(\"login-btn\")' not found\nTimeout exceeded"
        result = parse_ci_log(log)
        assert isinstance(result["selector_errors"], list)
        assert result["timeout_detected"] is True

    def test_classify_locator_stale(self):
        from agents.detective.tools import classify_failure
        result = classify_failure({
            "selector_errors": ["locator not found"],
            "assertion_errors": [],
            "env_errors": [],
            "timeout_detected": False,
        })
        assert result == "LOCATOR_STALE"

    def test_classify_env_failure(self):
        from agents.detective.tools import classify_failure
        result = classify_failure({
            "selector_errors": [],
            "assertion_errors": [],
            "env_errors": ["ECONNREFUSED"],
            "timeout_detected": False,
        })
        assert result == "ENV_FAILURE"

    def test_classify_timing_flake(self):
        from agents.detective.tools import classify_failure
        result = classify_failure({
            "selector_errors": [],
            "assertion_errors": [],
            "env_errors": [],
            "timeout_detected": True,
        })
        assert result == "TIMING_FLAKE"


class TestJudgeTools:
    def test_lint_gherkin_valid(self):
        from agents.judge.tools import lint_gherkin
        content = (
            "Feature: Login\n"
            "  Scenario: Valid login\n"
            "    Given the user is on the login page\n"
            "    When the user submits valid credentials\n"
            "    Then the user is redirected to dashboard\n"
        )
        result = lint_gherkin(content)
        assert result["has_feature"] is True
        assert result["has_scenario"] is True
        assert result["has_given"] is True
        assert result["has_when"] is True
        assert result["has_then"] is True

    def test_lint_gherkin_missing_feature(self):
        from agents.judge.tools import lint_gherkin
        result = lint_gherkin("Scenario: Something\n  Given something")
        assert result["has_feature"] is False

    def test_check_code_quality_clean(self):
        from agents.judge.tools import check_code_quality
        content = (
            "export class LoginPage extends BasePage {\n"
            "  private readonly btn = () => this.page.getByTestId('login-btn');\n"
            "  async navigate() { await this.page.goto('/login'); }\n"
            "}\n"
        )
        result = check_code_quality(content)
        assert result["no_sleep"] is True
        assert result["uses_testid_or_role"] is True
        assert result["has_class"] is True

    def test_check_code_quality_detects_sleep(self):
        from agents.judge.tools import check_code_quality
        content = "await page.waitForTimeout(2000);\nclass MyPage {}"
        result = check_code_quality(content)
        assert result["no_sleep"] is False

    def test_score_confidence(self):
        from agents.judge.tools import score_confidence
        results = {"has_feature": True, "has_scenario": True, "has_given_when_then": True,
                   "has_ac_tags": True, "no_technical_jargon": True}
        score = score_confidence(results, "gherkin")
        assert 0.0 <= score <= 1.0
        assert score > 0.8


class TestDiscoveryTools:
    def test_hash_content(self):
        from agents.discovery.tools import _hash_content
        h = _hash_content("hello world")
        assert len(h) == 16
        assert h == _hash_content("hello world")
        assert h != _hash_content("different content")

    def test_classify_component(self):
        from agents.discovery.tools import _classify_component
        result = _classify_component("button", None, None)
        assert result == "button"
        result_submit = _classify_component("input", "submit", None)
        assert result_submit == "button"
        result_link = _classify_component("a", None, None)
        assert result_link == "link"

    def test_infer_role(self):
        from agents.discovery.tools import _infer_role
        assert _infer_role("input", None) == "textbox"
        assert _infer_role("input", "checkbox") == "checkbox"
        assert _infer_role("button", None) == "button"
        assert _infer_role("a", None) == "link"

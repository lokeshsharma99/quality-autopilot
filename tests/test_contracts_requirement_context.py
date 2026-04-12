"""
Tests for contracts/requirement_context.py
===========================================

Tests for AcceptanceCriterionStatus, AcceptanceCriterionPriority,
AcceptanceCriterion, and RequirementContext Pydantic models.
"""

import pytest
from pydantic import ValidationError

from contracts.requirement_context import (
    AcceptanceCriterion,
    AcceptanceCriterionPriority,
    AcceptanceCriterionStatus,
    RequirementContext,
)


# ---------------------------------------------------------------------------
# AcceptanceCriterionStatus Tests
# ---------------------------------------------------------------------------


class TestAcceptanceCriterionStatus:
    def test_all_enum_values_exist(self):
        assert AcceptanceCriterionStatus.NOT_STARTED == "not_started"
        assert AcceptanceCriterionStatus.IN_PROGRESS == "in_progress"
        assert AcceptanceCriterionStatus.PASSED == "passed"
        assert AcceptanceCriterionStatus.FAILED == "failed"

    def test_enum_is_str_subclass(self):
        assert isinstance(AcceptanceCriterionStatus.NOT_STARTED, str)

    def test_enum_values_are_lowercase(self):
        for member in AcceptanceCriterionStatus:
            assert member.value == member.value.lower()


# ---------------------------------------------------------------------------
# AcceptanceCriterionPriority Tests
# ---------------------------------------------------------------------------


class TestAcceptanceCriterionPriority:
    def test_all_enum_values_exist(self):
        assert AcceptanceCriterionPriority.CRITICAL == "critical"
        assert AcceptanceCriterionPriority.HIGH == "high"
        assert AcceptanceCriterionPriority.MEDIUM == "medium"
        assert AcceptanceCriterionPriority.LOW == "low"

    def test_enum_is_str_subclass(self):
        assert isinstance(AcceptanceCriterionPriority.HIGH, str)

    def test_four_priority_levels(self):
        assert len(AcceptanceCriterionPriority) == 4


# ---------------------------------------------------------------------------
# AcceptanceCriterion Tests
# ---------------------------------------------------------------------------


class TestAcceptanceCriterion:
    def test_minimal_creation_with_criterion_only(self):
        ac = AcceptanceCriterion(criterion="User can log in")
        assert ac.criterion == "User can log in"
        assert ac.status == AcceptanceCriterionStatus.NOT_STARTED
        assert ac.priority == AcceptanceCriterionPriority.MEDIUM

    def test_explicit_status_and_priority(self):
        ac = AcceptanceCriterion(
            criterion="Form validates email",
            status=AcceptanceCriterionStatus.PASSED,
            priority=AcceptanceCriterionPriority.HIGH,
        )
        assert ac.status == AcceptanceCriterionStatus.PASSED
        assert ac.priority == AcceptanceCriterionPriority.HIGH

    def test_status_accepts_string_value(self):
        ac = AcceptanceCriterion(criterion="Test", status="in_progress")
        assert ac.status == AcceptanceCriterionStatus.IN_PROGRESS

    def test_priority_accepts_string_value(self):
        ac = AcceptanceCriterion(criterion="Test", priority="critical")
        assert ac.priority == AcceptanceCriterionPriority.CRITICAL

    def test_missing_criterion_raises_validation_error(self):
        with pytest.raises(ValidationError):
            AcceptanceCriterion()

    def test_invalid_status_raises_validation_error(self):
        with pytest.raises(ValidationError):
            AcceptanceCriterion(criterion="Test", status="unknown_status")

    def test_invalid_priority_raises_validation_error(self):
        with pytest.raises(ValidationError):
            AcceptanceCriterion(criterion="Test", priority="ultra_critical")

    def test_default_status_is_not_started(self):
        ac = AcceptanceCriterion(criterion="Any criterion")
        assert ac.status == AcceptanceCriterionStatus.NOT_STARTED

    def test_default_priority_is_medium(self):
        ac = AcceptanceCriterion(criterion="Any criterion")
        assert ac.priority == AcceptanceCriterionPriority.MEDIUM

    def test_serialization_to_dict(self):
        ac = AcceptanceCriterion(
            criterion="User can submit form",
            status=AcceptanceCriterionStatus.NOT_STARTED,
            priority=AcceptanceCriterionPriority.HIGH,
        )
        data = ac.model_dump()
        assert data["criterion"] == "User can submit form"
        assert data["status"] == "not_started"
        assert data["priority"] == "high"

    def test_creation_from_dict(self):
        data = {
            "criterion": "Redirect on success",
            "status": "passed",
            "priority": "critical",
        }
        ac = AcceptanceCriterion(**data)
        assert ac.criterion == "Redirect on success"
        assert ac.status == AcceptanceCriterionStatus.PASSED
        assert ac.priority == AcceptanceCriterionPriority.CRITICAL


# ---------------------------------------------------------------------------
# RequirementContext Tests
# ---------------------------------------------------------------------------


class TestRequirementContext:
    def _minimal_context(self):
        return RequirementContext(
            ticket_id="QA-123",
            title="User Login",
            description="Allow users to log in with email and password.",
        )

    def test_minimal_creation(self):
        ctx = self._minimal_context()
        assert ctx.ticket_id == "QA-123"
        assert ctx.title == "User Login"
        assert ctx.description == "Allow users to log in with email and password."

    def test_defaults_are_correct(self):
        ctx = self._minimal_context()
        assert ctx.ticket_url == ""
        assert ctx.acceptance_criteria == []
        assert ctx.affected_page_objects == []
        assert ctx.is_new_feature is False
        assert ctx.execution_plan == ""
        assert ctx.priority == AcceptanceCriterionPriority.MEDIUM
        assert ctx.estimated_complexity == ""
        assert ctx.dependencies == []

    def test_ticket_id_is_required(self):
        with pytest.raises(ValidationError):
            RequirementContext(title="T", description="D")

    def test_title_is_required(self):
        with pytest.raises(ValidationError):
            RequirementContext(ticket_id="QA-1", description="D")

    def test_description_is_required(self):
        with pytest.raises(ValidationError):
            RequirementContext(ticket_id="QA-1", title="T")

    def test_ticket_url_set_explicitly(self):
        ctx = RequirementContext(
            ticket_id="QA-123",
            ticket_url="https://jira.example.com/browse/QA-123",
            title="T",
            description="D",
        )
        assert ctx.ticket_url == "https://jira.example.com/browse/QA-123"

    def test_acceptance_criteria_with_acceptance_criterion_objects(self):
        ac1 = AcceptanceCriterion(criterion="AC 1", priority=AcceptanceCriterionPriority.HIGH)
        ac2 = AcceptanceCriterion(criterion="AC 2", priority=AcceptanceCriterionPriority.LOW)
        ctx = RequirementContext(
            ticket_id="QA-1",
            title="T",
            description="D",
            acceptance_criteria=[ac1, ac2],
        )
        assert len(ctx.acceptance_criteria) == 2
        assert ctx.acceptance_criteria[0].criterion == "AC 1"
        assert ctx.acceptance_criteria[1].priority == AcceptanceCriterionPriority.LOW

    def test_acceptance_criteria_from_dicts(self):
        ctx = RequirementContext(
            ticket_id="QA-1",
            title="T",
            description="D",
            acceptance_criteria=[
                {"criterion": "Validate email", "status": "not_started", "priority": "high"},
            ],
        )
        assert len(ctx.acceptance_criteria) == 1
        assert ctx.acceptance_criteria[0].criterion == "Validate email"

    def test_affected_page_objects_list(self):
        ctx = RequirementContext(
            ticket_id="QA-1",
            title="T",
            description="D",
            affected_page_objects=["LoginPage.ts", "DashboardPage.ts"],
        )
        assert "LoginPage.ts" in ctx.affected_page_objects
        assert "DashboardPage.ts" in ctx.affected_page_objects
        assert len(ctx.affected_page_objects) == 2

    def test_is_new_feature_true(self):
        ctx = RequirementContext(
            ticket_id="QA-1",
            title="T",
            description="D",
            is_new_feature=True,
        )
        assert ctx.is_new_feature is True

    def test_priority_field(self):
        ctx = RequirementContext(
            ticket_id="QA-1",
            title="T",
            description="D",
            priority=AcceptanceCriterionPriority.CRITICAL,
        )
        assert ctx.priority == AcceptanceCriterionPriority.CRITICAL

    def test_priority_from_string(self):
        ctx = RequirementContext(
            ticket_id="QA-1",
            title="T",
            description="D",
            priority="low",
        )
        assert ctx.priority == AcceptanceCriterionPriority.LOW

    def test_invalid_priority_raises_validation_error(self):
        with pytest.raises(ValidationError):
            RequirementContext(
                ticket_id="QA-1",
                title="T",
                description="D",
                priority="urgent",
            )

    def test_dependencies_list(self):
        ctx = RequirementContext(
            ticket_id="QA-1",
            title="T",
            description="D",
            dependencies=["QA-100", "QA-101"],
        )
        assert ctx.dependencies == ["QA-100", "QA-101"]

    def test_serialization_round_trip(self):
        original = RequirementContext(
            ticket_id="GDS-4",
            ticket_url="https://jira.example.com/browse/GDS-4",
            title="Personal Details Form",
            description="Implement the personal details step.",
            acceptance_criteria=[
                AcceptanceCriterion(
                    criterion="All fields visible",
                    status=AcceptanceCriterionStatus.NOT_STARTED,
                    priority=AcceptanceCriterionPriority.HIGH,
                )
            ],
            affected_page_objects=["PersonalDetailsPage.ts"],
            is_new_feature=True,
            execution_plan="Step 1: Create page object",
            priority=AcceptanceCriterionPriority.HIGH,
            estimated_complexity="medium",
            dependencies=["GDS-3"],
        )
        data = original.model_dump()
        restored = RequirementContext(**data)
        assert restored.ticket_id == original.ticket_id
        assert restored.title == original.title
        assert len(restored.acceptance_criteria) == 1
        assert restored.acceptance_criteria[0].criterion == "All fields visible"
        assert restored.is_new_feature is True
        assert restored.priority == AcceptanceCriterionPriority.HIGH

    def test_execution_plan_field(self):
        ctx = RequirementContext(
            ticket_id="QA-1",
            title="T",
            description="D",
            execution_plan="Step 1: Analyze. Step 2: Implement. Step 3: Test.",
        )
        assert "Step 1" in ctx.execution_plan

    def test_estimated_complexity_field(self):
        ctx = RequirementContext(
            ticket_id="QA-1",
            title="T",
            description="D",
            estimated_complexity="high",
        )
        assert ctx.estimated_complexity == "high"

    def test_empty_acceptance_criteria_list(self):
        ctx = RequirementContext(
            ticket_id="QA-1",
            title="T",
            description="D",
            acceptance_criteria=[],
        )
        assert ctx.acceptance_criteria == []

    def test_json_schema_generation(self):
        schema = RequirementContext.model_json_schema()
        assert "ticket_id" in schema["properties"]
        assert "acceptance_criteria" in schema["properties"]
        assert "affected_page_objects" in schema["properties"]
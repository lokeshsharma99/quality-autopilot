"""
Tests for contracts/judge_verdict.py
======================================

Tests for ChecklistResult, RejectionReason, and JudgeVerdict Pydantic models.
"""

import pytest
from pydantic import ValidationError

from contracts.judge_verdict import (
    ChecklistResult,
    JudgeVerdict,
    RejectionReason,
)


# ---------------------------------------------------------------------------
# RejectionReason Enum Tests
# ---------------------------------------------------------------------------


class TestRejectionReason:
    def test_all_enum_values_exist(self):
        assert RejectionReason.SYNTAX_ERROR == "syntax_error"
        assert RejectionReason.UNCLEAR_REQUIREMENTS == "unclear_requirements"
        assert RejectionReason.MISSING_TRACEABILITY == "missing_traceability"
        assert RejectionReason.NON_REUSABLE_STEPS == "non_reusable_steps"
        assert RejectionReason.INSUFFICIENT_COVERAGE == "insufficient_coverage"
        assert RejectionReason.DATA_REQUIREMENTS_MISSING == "data_requirements_missing"
        assert RejectionReason.OTHER == "other"

    def test_enum_is_str_subclass(self):
        assert isinstance(RejectionReason.SYNTAX_ERROR, str)

    def test_seven_rejection_reasons(self):
        assert len(RejectionReason) == 7

    def test_values_are_snake_case(self):
        for member in RejectionReason:
            assert member.value == member.value.lower()
            assert " " not in member.value


# ---------------------------------------------------------------------------
# ChecklistResult Tests
# ---------------------------------------------------------------------------


class TestChecklistResult:
    def test_minimal_creation(self):
        result = ChecklistResult(check_item="Syntax Validation", passed=True)
        assert result.check_item == "Syntax Validation"
        assert result.passed is True
        assert result.notes == ""

    def test_failed_with_notes(self):
        result = ChecklistResult(
            check_item="Traceability",
            passed=False,
            notes="No ticket_id found in the spec",
        )
        assert result.passed is False
        assert result.notes == "No ticket_id found in the spec"

    def test_missing_check_item_raises_error(self):
        with pytest.raises(ValidationError):
            ChecklistResult(passed=True)

    def test_missing_passed_raises_error(self):
        with pytest.raises(ValidationError):
            ChecklistResult(check_item="Syntax")

    def test_default_notes_is_empty_string(self):
        result = ChecklistResult(check_item="BA-Readability", passed=True)
        assert result.notes == ""

    def test_serialization_to_dict(self):
        result = ChecklistResult(
            check_item="Step Reusability",
            passed=False,
            notes="Hard-coded email on line 3",
        )
        data = result.model_dump()
        assert data["check_item"] == "Step Reusability"
        assert data["passed"] is False
        assert data["notes"] == "Hard-coded email on line 3"


# ---------------------------------------------------------------------------
# JudgeVerdict Tests
# ---------------------------------------------------------------------------


class TestJudgeVerdict:
    def _minimal_verdict(self, confidence=95.0, passed=True):
        return JudgeVerdict(
            confidence=confidence,
            passed=passed,
            timestamp="2026-04-12T10:00:00Z",
        )

    def test_minimal_creation(self):
        verdict = self._minimal_verdict()
        assert verdict.confidence == 95.0
        assert verdict.passed is True
        assert verdict.timestamp == "2026-04-12T10:00:00Z"

    def test_defaults(self):
        verdict = self._minimal_verdict()
        assert verdict.checklist_results == []
        assert verdict.rejection_reasons == []
        assert verdict.requires_human is False
        assert verdict.reviewed_item_type == ""
        assert verdict.reviewed_item_id == ""
        assert verdict.feedback == ""

    def test_confidence_boundary_zero(self):
        verdict = self._minimal_verdict(confidence=0.0, passed=False)
        assert verdict.confidence == 0.0

    def test_confidence_boundary_one_hundred(self):
        verdict = self._minimal_verdict(confidence=100.0, passed=True)
        assert verdict.confidence == 100.0

    def test_confidence_below_zero_raises_error(self):
        with pytest.raises(ValidationError):
            JudgeVerdict(confidence=-1.0, passed=True, timestamp="2026-04-12T10:00:00Z")

    def test_confidence_above_one_hundred_raises_error(self):
        with pytest.raises(ValidationError):
            JudgeVerdict(confidence=100.1, passed=True, timestamp="2026-04-12T10:00:00Z")

    def test_confidence_exactly_at_auto_approve_threshold(self):
        verdict = self._minimal_verdict(confidence=90.0)
        assert verdict.confidence == 90.0

    def test_confidence_just_below_threshold(self):
        verdict = self._minimal_verdict(confidence=89.9, passed=False)
        assert verdict.confidence == 89.9

    def test_missing_confidence_raises_error(self):
        with pytest.raises(ValidationError):
            JudgeVerdict(passed=True, timestamp="2026-04-12T10:00:00Z")

    def test_missing_passed_raises_error(self):
        with pytest.raises(ValidationError):
            JudgeVerdict(confidence=90.0, timestamp="2026-04-12T10:00:00Z")

    def test_missing_timestamp_raises_error(self):
        with pytest.raises(ValidationError):
            JudgeVerdict(confidence=90.0, passed=True)

    def test_with_checklist_results(self):
        results = [
            ChecklistResult(check_item="Syntax", passed=True),
            ChecklistResult(check_item="Traceability", passed=False, notes="Missing @ticket tag"),
        ]
        verdict = JudgeVerdict(
            confidence=70.0,
            passed=False,
            timestamp="2026-04-12T10:00:00Z",
            checklist_results=results,
        )
        assert len(verdict.checklist_results) == 2
        assert verdict.checklist_results[0].passed is True
        assert verdict.checklist_results[1].notes == "Missing @ticket tag"

    def test_with_rejection_reasons(self):
        verdict = JudgeVerdict(
            confidence=55.0,
            passed=False,
            timestamp="2026-04-12T10:00:00Z",
            rejection_reasons=[
                RejectionReason.MISSING_TRACEABILITY,
                RejectionReason.NON_REUSABLE_STEPS,
            ],
        )
        assert len(verdict.rejection_reasons) == 2
        assert RejectionReason.MISSING_TRACEABILITY in verdict.rejection_reasons

    def test_rejection_reasons_from_strings(self):
        verdict = JudgeVerdict(
            confidence=50.0,
            passed=False,
            timestamp="2026-04-12T10:00:00Z",
            rejection_reasons=["syntax_error", "other"],
        )
        assert verdict.rejection_reasons[0] == RejectionReason.SYNTAX_ERROR

    def test_invalid_rejection_reason_raises_error(self):
        with pytest.raises(ValidationError):
            JudgeVerdict(
                confidence=50.0,
                passed=False,
                timestamp="2026-04-12T10:00:00Z",
                rejection_reasons=["not_a_real_reason"],
            )

    def test_requires_human_flag(self):
        verdict = JudgeVerdict(
            confidence=85.0,
            passed=False,
            timestamp="2026-04-12T10:00:00Z",
            requires_human=True,
        )
        assert verdict.requires_human is True

    def test_reviewed_item_type_and_id(self):
        verdict = JudgeVerdict(
            confidence=92.0,
            passed=True,
            timestamp="2026-04-12T10:00:00Z",
            reviewed_item_type="GherkinSpec",
            reviewed_item_id="GDS-4",
        )
        assert verdict.reviewed_item_type == "GherkinSpec"
        assert verdict.reviewed_item_id == "GDS-4"

    def test_feedback_field(self):
        verdict = JudgeVerdict(
            confidence=60.0,
            passed=False,
            timestamp="2026-04-12T10:00:00Z",
            feedback="Step on line 5 has a hard-coded email address. Please parameterize it.",
        )
        assert "hard-coded" in verdict.feedback

    def test_serialization_round_trip(self):
        original = JudgeVerdict(
            confidence=92.5,
            passed=True,
            checklist_results=[
                ChecklistResult(check_item="Syntax Validation", passed=True),
                ChecklistResult(check_item="BA-Readability", passed=True, notes="Excellent business language"),
                ChecklistResult(check_item="Traceability", passed=True),
            ],
            rejection_reasons=[],
            requires_human=False,
            timestamp="2026-04-12T10:00:00Z",
            reviewed_item_type="GherkinSpec",
            reviewed_item_id="QA-123",
            feedback="",
        )
        data = original.model_dump()
        restored = JudgeVerdict(**data)
        assert restored.confidence == 92.5
        assert restored.passed is True
        assert len(restored.checklist_results) == 3
        assert restored.checklist_results[1].notes == "Excellent business language"
        assert restored.reviewed_item_id == "QA-123"

    def test_failed_verdict_with_all_fields(self):
        verdict = JudgeVerdict(
            confidence=35.0,
            passed=False,
            checklist_results=[
                ChecklistResult(check_item="Syntax Validation", passed=False, notes="Missing Feature keyword"),
                ChecklistResult(check_item="Traceability", passed=False, notes="No ticket tag"),
            ],
            rejection_reasons=[RejectionReason.SYNTAX_ERROR, RejectionReason.MISSING_TRACEABILITY],
            requires_human=True,
            timestamp="2026-04-12T10:00:00Z",
            reviewed_item_type="GherkinSpec",
            reviewed_item_id="QA-999",
            feedback="Spec has syntax errors and missing traceability. Needs full rewrite.",
        )
        assert verdict.confidence == 35.0
        assert verdict.passed is False
        assert len(verdict.rejection_reasons) == 2
        assert verdict.requires_human is True

    def test_float_precision_confidence(self):
        verdict = self._minimal_verdict(confidence=89.999)
        assert verdict.confidence == pytest.approx(89.999)

    def test_zero_confidence_verdict(self):
        verdict = JudgeVerdict(
            confidence=0.0,
            passed=False,
            timestamp="2026-04-12T10:00:00Z",
            rejection_reasons=[RejectionReason.SYNTAX_ERROR],
            feedback="Spec is completely invalid.",
        )
        assert verdict.confidence == 0.0
        assert verdict.passed is False
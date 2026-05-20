"""
Tests for contracts/__init__.py
=================================

Verifies that the contracts package correctly exports all required models.
"""

import contracts


class TestContractsPackageExports:
    def test_requirement_context_exported(self):
        from contracts import RequirementContext
        assert RequirementContext is not None

    def test_gherkin_spec_exported(self):
        from contracts import GherkinSpec
        assert GherkinSpec is not None

    def test_judge_verdict_exported(self):
        from contracts import JudgeVerdict
        assert JudgeVerdict is not None

    def test_all_contains_expected_names(self):
        expected = {"RequirementContext", "GherkinSpec", "JudgeVerdict", "SiteManifesto"}
        assert set(contracts.__all__) == expected

    def test_requirement_context_is_importable_from_package(self):
        from contracts import RequirementContext
        ctx = RequirementContext(
            ticket_id="PKG-1",
            title="Package test",
            description="Verify import works",
        )
        assert ctx.ticket_id == "PKG-1"

    def test_gherkin_spec_is_importable_from_package(self):
        from contracts import GherkinSpec
        spec = GherkinSpec(
            feature_name="Package Feature",
            feature_description="Tests the package import",
        )
        assert spec.feature_name == "Package Feature"

    def test_judge_verdict_is_importable_from_package(self):
        from contracts import JudgeVerdict
        verdict = JudgeVerdict(
            confidence=90.0,
            passed=True,
            timestamp="2026-04-12T00:00:00Z",
        )
        assert verdict.confidence == 90.0

    def test_exported_names_are_the_correct_classes(self):
        from contracts import RequirementContext, GherkinSpec, JudgeVerdict
        from contracts.requirement_context import RequirementContext as RC
        from contracts.gherkin_spec import GherkinSpec as GS
        from contracts.judge_verdict import JudgeVerdict as JV

        assert RequirementContext is RC
        assert GherkinSpec is GS
        assert JudgeVerdict is JV
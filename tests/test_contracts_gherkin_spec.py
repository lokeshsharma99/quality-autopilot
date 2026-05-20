"""
Tests for contracts/gherkin_spec.py
=====================================

Tests for DataType, DataRequirement, StepType, GherkinStep,
GherkinScenario, and GherkinSpec Pydantic models.
"""

import pytest
from pydantic import ValidationError

from contracts.gherkin_spec import (
    DataRequirement,
    DataType,
    GherkinScenario,
    GherkinSpec,
    GherkinStep,
    StepType,
)


# ---------------------------------------------------------------------------
# DataType Enum Tests
# ---------------------------------------------------------------------------


class TestDataType:
    def test_all_enum_values_exist(self):
        assert DataType.STRING == "string"
        assert DataType.NUMBER == "number"
        assert DataType.EMAIL == "email"
        assert DataType.URL == "url"
        assert DataType.DATE == "date"
        assert DataType.BOOLEAN == "boolean"
        assert DataType.ENUM == "enum"

    def test_enum_is_str_subclass(self):
        assert isinstance(DataType.STRING, str)

    def test_seven_data_types(self):
        assert len(DataType) == 7


# ---------------------------------------------------------------------------
# StepType Enum Tests
# ---------------------------------------------------------------------------


class TestStepType:
    def test_all_enum_values_exist(self):
        assert StepType.GIVEN == "Given"
        assert StepType.WHEN == "When"
        assert StepType.THEN == "Then"
        assert StepType.AND == "And"
        assert StepType.BUT == "But"

    def test_enum_is_str_subclass(self):
        assert isinstance(StepType.GIVEN, str)

    def test_five_step_types(self):
        assert len(StepType) == 5

    def test_values_are_capitalized(self):
        for member in StepType:
            assert member.value[0].isupper()


# ---------------------------------------------------------------------------
# DataRequirement Tests
# ---------------------------------------------------------------------------


class TestDataRequirement:
    def test_minimal_creation(self):
        dr = DataRequirement(
            field_name="username",
            data_type=DataType.STRING,
            example_value="john.doe",
        )
        assert dr.field_name == "username"
        assert dr.data_type == DataType.STRING
        assert dr.example_value == "john.doe"

    def test_defaults(self):
        dr = DataRequirement(
            field_name="email",
            data_type=DataType.EMAIL,
            example_value="user@example.com",
        )
        assert dr.source == ""
        assert dr.is_required is True

    def test_optional_source(self):
        dr = DataRequirement(
            field_name="email",
            data_type=DataType.EMAIL,
            example_value="user@example.com",
            source="ticket description",
        )
        assert dr.source == "ticket description"

    def test_is_required_false(self):
        dr = DataRequirement(
            field_name="middle_name",
            data_type=DataType.STRING,
            example_value="",
            is_required=False,
        )
        assert dr.is_required is False

    def test_data_type_from_string(self):
        dr = DataRequirement(
            field_name="age",
            data_type="number",
            example_value="25",
        )
        assert dr.data_type == DataType.NUMBER

    def test_invalid_data_type_raises_error(self):
        with pytest.raises(ValidationError):
            DataRequirement(
                field_name="x",
                data_type="invalid_type",
                example_value="val",
            )

    def test_missing_required_fields_raises_error(self):
        with pytest.raises(ValidationError):
            DataRequirement(field_name="x")

    def test_url_data_type(self):
        dr = DataRequirement(
            field_name="redirect_url",
            data_type=DataType.URL,
            example_value="https://example.com/dashboard",
        )
        assert dr.data_type == DataType.URL

    def test_date_data_type(self):
        dr = DataRequirement(
            field_name="dob",
            data_type=DataType.DATE,
            example_value="1990-01-15",
        )
        assert dr.data_type == DataType.DATE

    def test_serialization_to_dict(self):
        dr = DataRequirement(
            field_name="ni_number",
            data_type=DataType.STRING,
            example_value="QQ123456C",
            source="ticket",
            is_required=True,
        )
        data = dr.model_dump()
        assert data["field_name"] == "ni_number"
        assert data["data_type"] == "string"
        assert data["example_value"] == "QQ123456C"


# ---------------------------------------------------------------------------
# GherkinStep Tests
# ---------------------------------------------------------------------------


class TestGherkinStep:
    def test_minimal_creation(self):
        step = GherkinStep(step_type=StepType.GIVEN, text="I am on the login page")
        assert step.step_type == StepType.GIVEN
        assert step.text == "I am on the login page"
        assert step.is_reusable is True

    def test_is_reusable_false(self):
        step = GherkinStep(
            step_type=StepType.WHEN,
            text='I enter "hardcoded@email.com"',
            is_reusable=False,
        )
        assert step.is_reusable is False

    def test_step_type_from_string(self):
        step = GherkinStep(step_type="Then", text="I should see a success message")
        assert step.step_type == StepType.THEN

    def test_invalid_step_type_raises_error(self):
        with pytest.raises(ValidationError):
            GherkinStep(step_type="Invalid", text="some text")

    def test_missing_text_raises_error(self):
        with pytest.raises(ValidationError):
            GherkinStep(step_type=StepType.GIVEN)

    def test_and_step_type(self):
        step = GherkinStep(step_type=StepType.AND, text="the form is submitted")
        assert step.step_type == StepType.AND

    def test_but_step_type(self):
        step = GherkinStep(step_type=StepType.BUT, text="the session is not cleared")
        assert step.step_type == StepType.BUT


# ---------------------------------------------------------------------------
# GherkinScenario Tests
# ---------------------------------------------------------------------------


class TestGherkinScenario:
    def test_minimal_creation(self):
        scenario = GherkinScenario(name="Successful login")
        assert scenario.name == "Successful login"
        assert scenario.description == ""
        assert scenario.steps == []
        assert scenario.data_requirements == []

    def test_with_steps(self):
        steps = [
            GherkinStep(step_type=StepType.GIVEN, text="I am on the login page"),
            GherkinStep(step_type=StepType.WHEN, text="I submit credentials"),
            GherkinStep(step_type=StepType.THEN, text="I see the dashboard"),
        ]
        scenario = GherkinScenario(name="Happy path", steps=steps)
        assert len(scenario.steps) == 3
        assert scenario.steps[0].step_type == StepType.GIVEN
        assert scenario.steps[2].step_type == StepType.THEN

    def test_with_data_requirements(self):
        dr = DataRequirement(
            field_name="password",
            data_type=DataType.STRING,
            example_value="s3cr3t",
        )
        scenario = GherkinScenario(name="Test", data_requirements=[dr])
        assert len(scenario.data_requirements) == 1
        assert scenario.data_requirements[0].field_name == "password"

    def test_missing_name_raises_error(self):
        with pytest.raises(ValidationError):
            GherkinScenario()

    def test_description_optional(self):
        scenario = GherkinScenario(name="Test", description="This tests the happy path")
        assert scenario.description == "This tests the happy path"


# ---------------------------------------------------------------------------
# GherkinSpec Tests
# ---------------------------------------------------------------------------


class TestGherkinSpec:
    def _minimal_spec(self):
        return GherkinSpec(
            feature_name="User Authentication",
            feature_description="Allows users to log in to the application",
        )

    def test_minimal_creation(self):
        spec = self._minimal_spec()
        assert spec.feature_name == "User Authentication"
        assert spec.feature_description == "Allows users to log in to the application"

    def test_defaults(self):
        spec = self._minimal_spec()
        assert spec.scenarios == []
        assert spec.data_requirements == []
        assert spec.traceability == {}
        assert spec.file_path == ""
        assert spec.tags == []

    def test_missing_feature_name_raises_error(self):
        with pytest.raises(ValidationError):
            GherkinSpec(feature_description="desc")

    def test_missing_feature_description_raises_error(self):
        with pytest.raises(ValidationError):
            GherkinSpec(feature_name="name")

    def test_with_scenarios(self):
        scenario = GherkinScenario(
            name="Login with valid credentials",
            steps=[
                GherkinStep(step_type=StepType.GIVEN, text="I am on the login page"),
                GherkinStep(step_type=StepType.THEN, text="I am logged in"),
            ],
        )
        spec = GherkinSpec(
            feature_name="Authentication",
            feature_description="Login feature",
            scenarios=[scenario],
        )
        assert len(spec.scenarios) == 1
        assert spec.scenarios[0].name == "Login with valid credentials"

    def test_traceability_dict(self):
        spec = GherkinSpec(
            feature_name="Feature",
            feature_description="Desc",
            traceability={"ticket_id": "QA-123", "requirement_context_id": "ctx-456"},
        )
        assert spec.traceability["ticket_id"] == "QA-123"
        assert spec.traceability["requirement_context_id"] == "ctx-456"

    def test_file_path(self):
        spec = GherkinSpec(
            feature_name="Feature",
            feature_description="Desc",
            file_path="automation/features/user-authentication.feature",
        )
        assert spec.file_path == "automation/features/user-authentication.feature"

    def test_tags_list(self):
        spec = GherkinSpec(
            feature_name="Feature",
            feature_description="Desc",
            tags=["@smoke", "@regression", "@GDS-4"],
        )
        assert "@smoke" in spec.tags
        assert "@regression" in spec.tags
        assert len(spec.tags) == 3

    def test_global_data_requirements(self):
        dr = DataRequirement(
            field_name="base_url",
            data_type=DataType.URL,
            example_value="https://app.example.com",
        )
        spec = GherkinSpec(
            feature_name="Feature",
            feature_description="Desc",
            data_requirements=[dr],
        )
        assert len(spec.data_requirements) == 1
        assert spec.data_requirements[0].data_type == DataType.URL

    def test_full_spec_serialization_round_trip(self):
        original = GherkinSpec(
            feature_name="Personal Details",
            feature_description="User enters personal details for UC application",
            scenarios=[
                GherkinScenario(
                    name="Submit valid details",
                    steps=[
                        GherkinStep(step_type=StepType.GIVEN, text="I am on the form"),
                        GherkinStep(step_type=StepType.WHEN, text="I fill in {name}"),
                        GherkinStep(step_type=StepType.THEN, text="I proceed to next step"),
                    ],
                    data_requirements=[
                        DataRequirement(
                            field_name="name",
                            data_type=DataType.STRING,
                            example_value="John Smith",
                        )
                    ],
                )
            ],
            traceability={"ticket_id": "GDS-4"},
            file_path="automation/features/GDS-4-personal-details.feature",
            tags=["@GDS-4", "@smoke"],
        )
        data = original.model_dump()
        restored = GherkinSpec(**data)
        assert restored.feature_name == "Personal Details"
        assert len(restored.scenarios) == 1
        assert restored.scenarios[0].steps[1].text == "I fill in {name}"
        assert restored.traceability["ticket_id"] == "GDS-4"

    def test_traceability_with_multiple_keys(self):
        spec = GherkinSpec(
            feature_name="Feature",
            feature_description="Desc",
            traceability={
                "ticket_id": "GDS-4",
                "epic": "EP-1",
                "sprint": "Sprint-7",
            },
        )
        assert len(spec.traceability) == 3

    def test_empty_scenarios_default(self):
        spec = GherkinSpec(
            feature_name="Feature",
            feature_description="Desc",
            scenarios=[],
        )
        assert spec.scenarios == []
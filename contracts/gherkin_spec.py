"""
GherkinSpec Contract
======================

Scribe agent output — BDD feature file + data requirements.
"""

from pydantic import BaseModel


class DataRequirement(BaseModel):
    field: str
    type: str
    constraints: str            # e.g., "unique email", "valid US phone"
    pii_mask: bool


class GherkinSpec(BaseModel):
    ticket_id: str
    feature_file: str           # Relative path to .feature file
    feature_content: str        # Full Gherkin text
    data_requirements: list[DataRequirement]
    traceability: dict[str, str]    # AC-ID → Scenario name mapping

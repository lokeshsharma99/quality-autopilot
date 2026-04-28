"""
AutomationScaffold Contract
============================

Automation scaffolding contract — describes what the Engineer should scaffold.
"""

from pydantic import BaseModel


class AutomationScaffold(BaseModel):
    ticket_id: str
    feature_file_path: str          # e.g., "features/login.feature"
    pom_file_paths: list[str]       # e.g., ["pages/login.page.ts"]
    step_def_file_paths: list[str]  # e.g., ["step_definitions/login.steps.ts"]
    scaffold_complete: bool

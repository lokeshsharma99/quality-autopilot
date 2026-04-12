"""
Automation Scaffold Contract
==============================

Contract for automation project scaffolding - structure and configuration
for BDD+POM framework initialization.
"""

from pydantic import BaseModel
from typing import Optional


class ScaffoldConfig(BaseModel):
    """Configuration for automation framework scaffolding."""
    project_name: str
    base_url: str
    browser: str = "chromium"
    headless: bool = True
    timeout: int = 30000
    viewport_width: int = 1280
    viewport_height: int = 720
    use_cucumber: bool = True
    use_playwright: bool = True


class ScaffoldStructure(BaseModel):
    """Directory structure created during scaffolding."""
    features_dir: str
    step_definitions_dir: str
    pages_dir: str
    config_dir: str
    tests_dir: str
    reports_dir: str
    hooks_dir: str


class ScaffoldFile(BaseModel):
    """File created during scaffolding."""
    path: str
    content: str
    file_type: str  # config, page, step, feature, hook


class AutomationScaffold(BaseModel):
    """Complete automation scaffold output."""
    project_name: str
    config: ScaffoldConfig
    structure: ScaffoldStructure
    files: list[ScaffoldFile]
    success: bool
    message: str
    created_at: str

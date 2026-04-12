"""
Automation Scaffold Workflow
============================

Workflow for scaffolding BDD+POM automation framework when a new project is initiated.
"""

from agno.workflow import Workflow, Step
from agents.engineer import engineer
from contracts.automation_scaffold import AutomationScaffold

# ---------------------------------------------------------------------------
# Create Workflow
# ---------------------------------------------------------------------------
automation_scaffold = Workflow(
    id="automation-scaffold",
    name="Automation Framework Scaffold",
    steps=[
        Step(
            name="Create Scaffold Structure",
            agent=engineer,
        ),
    ],
)

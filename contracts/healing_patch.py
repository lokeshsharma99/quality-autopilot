"""
HealingPatch Contract
======================

Medic agent output — surgical locator replacement.
verification_passes MUST be >= 3.
logic_changed MUST be False.
"""

from pydantic import BaseModel


class HealingPatch(BaseModel):
    test_name: str
    trace_id: str
    file_path: str              # Path to the patched POM file
    old_locator: str            # The broken locator that was replaced
    new_locator: str            # The working locator that replaced it
    diff: str                   # Unified diff format (human-reviewable)
    verification_passes: int    # Must be >= 3
    logic_changed: bool         # MUST be False

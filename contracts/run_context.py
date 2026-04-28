"""
RunContext Contract
====================

Data Agent output — everything the test environment needs to run a scenario.
"""

from pydantic import BaseModel


class TestUser(BaseModel):
    username: str
    email: str              # PII masked if needed
    password: str
    role: str               # e.g., "admin", "user", "guest"


class RunContext(BaseModel):
    """The Data Agent's output — validated test data fixtures with env context."""

    ticket_id: str
    test_users: list[TestUser]
    db_seed_queries: list[str]          # SQL statements for data setup
    api_mocks: dict[str, str]           # endpoint → mock response mapping
    cleanup_queries: list[str]          # SQL statements for teardown
    pii_masked: bool                    # Must be True
    unique_constraints_valid: bool      # Must be True

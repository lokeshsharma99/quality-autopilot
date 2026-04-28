---
applyTo: "agents/**/*.py"
---

# Agent Files — Copilot Instructions

These instructions apply to all Python files under `agents/`.

## Required File Layout

Every agent directory (`agents/<name>/`) must contain exactly:

```
agent.py          ← Agent definition (only file that instantiates Agent())
instructions.py   ← INSTRUCTIONS = """..."""  (prompt string, nothing else)
__init__.py       ← re-exports the agent instance
__main__.py       ← CLI runner: agent.cli()
tools.py          ← custom tools (only when the agent needs them)
```

## agent.py Template

```python
from agno.agent import Agent
# from agno.tools.xxx import XxxTools   ← add tools as needed

from agents.<name>.instructions import INSTRUCTIONS
from app.settings import MODEL, agent_db

# ---------------------------------------------------------------------------
# Tools   ← include this block only if agent has tools
# ---------------------------------------------------------------------------
# <tool_instance> = XxxTools(...)

# ---------------------------------------------------------------------------
# Create Agent
# ---------------------------------------------------------------------------
<name> = Agent(
    # Identity
    id="<name>",
    name="<Name>",

    # Model
    model=MODEL,

    # Data
    db=agent_db,

    # Capabilities
    tools=[...],
    learning=True,
    add_learnings_to_context=True,

    # Instructions
    instructions=INSTRUCTIONS,

    # Memory
    enable_agentic_memory=True,

    # Context
    add_datetime_to_context=True,
    add_history_to_context=True,
    read_chat_history=True,
    num_history_runs=5,

    # Output
    markdown=True,
)
```

## __init__.py Template

```python
from agents.<name>.agent import <name> as <name>
```

## __main__.py Template

```python
from agents.<name> import <name>

if __name__ == "__main__":
    <name>.cli()
```

## Rules

- Parameter order in `Agent()` is **mandatory** — see `AGENTS.md` Section IV.2.
- Section headers must be exactly 75 chars wide using `# ---` style.
- `INSTRUCTIONS` lives **only** in `instructions.py`. Never inline prompt strings in `agent.py`.
- `role=` is required only when the agent is used as a team member.
- All tools must be imported at the top of `agent.py`, not inside functions.
- Knowledge bases are created via `db/session.py::create_knowledge()` — never manually.
- `session_state` block comes after `instructions=` and before `enable_agentic_memory=True`.
- No `time.sleep()` anywhere in agent code.
- No hardcoded secrets — use `getenv()`.
- Every agent that produces an artifact must emit a Pydantic contract from `contracts/`.

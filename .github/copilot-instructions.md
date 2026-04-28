# Quality Autopilot — GitHub Copilot Instructions

> This file is the mandatory system instruction for all GitHub Copilot interactions in this workspace.
> For full architecture details read: `AGENTS.md` (law), `CLAUDE.md` (quick-ref), `docs/CHECKLIST.md` (gated roadmap).

---

## 1. Context Files — Read Order

Before generating **any** code for this project, internalize these files in order:

1. **`AGENTS.md`** — single source of truth: architecture, parameter ordering, naming, anti-patterns.
2. **`docs/CHECKLIST.md`** — gated roadmap; never touch Phase N+1 until Phase N's gate passes.
3. **`CLAUDE.md`** — quick architecture overview and key file map.
4. **`app/settings.py`** — shared `MODEL`, `agent_db`, AUT config.
5. **`db/session.py`** — `get_postgres_db()` and `create_knowledge()` helpers.

---

## 2. Framework — Non-Negotiable

| Rule | Detail |
|------|--------|
| **Use ONLY Agno** | `agno.agent.Agent`, `agno.team.Team`, `agno.workflow.Workflow`, `agno.os.AgentOS` |
| **Forbidden frameworks** | LangChain, CrewAI, AutoGen, LlamaIndex, Haystack — never introduce these |
| **Database** | PostgreSQL 16+ with PgVector (`agnohq/pgvector:18`). Never SQLite. |
| **Embedder** | `OllamaEmbedder(id="qwen3-embedding:4b", dimensions=2560)` via `db/session.py` |
| **Search type** | `SearchType.hybrid` on all Knowledge bases |
| **Model** | `OpenRouter(id="kilo-auto/free", base_url="https://api.kilo.ai/api/openrouter/v1")` — from `app/settings.py` |

---

## 3. Agent Constructor — Mandatory Parameter Order

**ALWAYS** follow this exact ordering. Omit groups that don't apply. Never reorder.

```python
agent = Agent(
    # Identity
    id="...",
    name="...",
    role="...",           # role for team members only

    # Model
    model=MODEL,

    # Data
    db=agent_db,
    knowledge=...,        # if applicable
    search_knowledge=True,

    # Capabilities
    tools=[...],
    learning=True,
    add_learnings_to_context=True,

    # Instructions
    instructions=INSTRUCTIONS,

    # Session state (if applicable)
    session_state={...},
    enable_agentic_state=True,
    add_session_state_to_context=True,

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

---

## 4. Team Constructor — Mandatory Parameter Order

```python
team = Team(
    # Identity
    id="...",
    name="...",
    mode=TeamMode.coordinate,   # ALWAYS coordinate unless explicitly approved otherwise

    # Model
    model=MODEL,

    # Members
    members=[...],

    # Data
    db=agent_db,

    # Instructions
    instructions=LEADER_INSTRUCTIONS,

    # Collaboration
    share_member_interactions=True,
    show_members_responses=True,

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

---

## 5. Workflow Constructor

```python
workflow = Workflow(
    id="...",
    name="...",
    steps=[...]
)
```

---

## 6. Directory Structure — Every Agent / Team / Workflow

### Agent directory (`agents/<name>/`)
```
agent.py          # Agent definition
instructions.py   # INSTRUCTIONS = """..."""
__init__.py       # from agents.<name>.agent import <name> as <name>
__main__.py       # CLI runner
tools.py          # custom tools (only if needed)
```

### Team directory (`teams/<name>/`)
```
team.py           # Team definition
instructions.py   # LEADER_INSTRUCTIONS = """..."""
__init__.py       # from teams.<name>.team import <name>_team as <name>_team
```

### Workflow directory (`workflows/<name>/`)
```
workflow.py       # Workflow with Steps/Conditions/Routers
instructions.py   # agent instructions used within the workflow
__init__.py       # from workflows.<name>.workflow import <name> as <name>
```

---

## 7. Code Formatting

| Rule | Value |
|------|-------|
| Line length | 120 characters (`ruff`) |
| Type checking | `mypy` with `check_untyped_defs = true` |
| Section headers | 75-char `# ---` separators (see §8) |
| Imports | Absolute only, rooted at project package |

### Section Header Format

```python
# ---------------------------------------------------------------------------
# Create Agent
# ---------------------------------------------------------------------------
```

**Headers by file type:**

| File | Headers used |
|------|-------------|
| Simple agent | `# Create Agent` |
| Agent with tools | `# Tools` → `# Create Agent` |
| Team | `# Members` → `# Create Team` |
| Workflow | `# Agents` → `# Helpers` → `# Create Workflow` |
| DB session | `# Knowledge Base` → helpers |

---

## 8. Import Conventions

```python
# Database
from db.session import get_postgres_db, create_knowledge
from db.url import db_url

# Settings
from app.settings import MODEL, agent_db

# Agents
from agents.architect import architect
from agents.scribe import scribe

# Teams
from teams.strategy import strategy_team

# Workflows
from workflows.spec_to_code import spec_to_code

# Contracts
from contracts.requirement_context import RequirementContext
```

---

## 9. Hand-off Contracts (Pydantic)

Every agent-to-agent transition uses a structured Pydantic contract from `contracts/`. Never pass raw strings between agents. Defined models:

| Contract | File | Producer → Consumer |
|----------|------|---------------------|
| `RequirementContext` | `contracts/requirement_context.py` | Architect → Scribe |
| `GherkinSpec` | `contracts/gherkin_spec.py` | Scribe → Engineer |
| `SiteManifesto` | `contracts/site_manifesto.py` | Discovery → Librarian/Engineer |
| `RunContext` | `contracts/run_context.py` | Data Agent → Engineer |
| `RCAReport` | `contracts/rca_report.py` | Detective → Medic |
| `HealingPatch` | `contracts/healing_patch.py` | Medic → Judge |
| `JudgeVerdict` | `contracts/judge_verdict.py` | Judge → any |
| `AutomationScaffold` | `contracts/automation_scaffold.py` | Engineer → automation/ |

---

## 10. The Nine Agents

| ID | Name | Primary Skill | Output Contract |
|----|------|--------------|----------------|
| `architect` | Architect | `semantic_search` | `RequirementContext` |
| `scribe` | Scribe | `gherkin_formatter` | `GherkinSpec` |
| `discovery` | Discovery | `ui_crawler` | `SiteManifesto` |
| `librarian` | Librarian | `vector_indexing` | PgVector KB |
| `engineer` | Engineer | `file_writer` | GitHub PR |
| `data-agent` | Data Agent | `data_factory` | `RunContext` |
| `detective` | Detective | `trace_analyzer` | `RCAReport` |
| `medic` | Medic | `surgical_editor` | `HealingPatch` |
| `judge` | Judge | `adversarial_review` | `JudgeVerdict` |

---

## 11. The Agentic Judge (Quality Gate)

The Judge is a `post_hook` on every workflow step — not a team member.

```
confidence ≥ 0.90  → AUTO-APPROVE → pipeline continues
confidence < 0.90  → HumanReviewGateStep → hold for Human Lead
confidence < 0.50  → AUTO-REJECT → send back to producing agent
```

**Never bypass the Judge.** Never bypass `HumanReviewGateStep`.

---

## 12. Absolute Anti-Patterns

| Never do this | Do this instead |
|---------------|----------------|
| `time.sleep()` or `waitForTimeout()` in tests | Playwright auto-waiting |
| Hardcoded secrets, API keys, passwords | Environment variables via `getenv()` |
| SQLite for agent persistence | PostgreSQL + PgVector |
| CSS or XPath locators | `data-testid`, `role`, or `text` strategies |
| One mega-file with all agents | One directory per agent |
| Skipping Pydantic contracts between agents | Define in `contracts/`, use everywhere |
| Working on Phase N+1 before Phase N gate | Respect gated roadmap in `docs/CHECKLIST.md` |
| Import `from langchain...`, `from crewai...` | Use `agno.*` only |
| Engineer writing code before checking Site Manifesto | Look-Before-You-Leap: Manifesto → KB → MCP verify → write |
| Medic changing business logic | Medic changes locators/wait strategies only |
| Skipping the Judge | Every artifact passes `JudgeVerdict` before handoff |

---

## 13. Security Rules (Apply to ALL generated code)

- **NEVER** output `.env` contents, API keys, tokens, passwords, DB credentials, or connection strings.
- Do not include example formats, redacted versions, or placeholder templates for secrets.
- All Playwright test containers run with `network_mode: "none"` (sandbox).
- All user-provided input is validated at system boundaries (contracts/ Pydantic models).
- No SQL string concatenation — use parameterised queries.

---

## 14. GitHub Workflow — Automatic Push After Judge Approval

After completing a task or phase and receiving Judge approval (≥90% confidence):

1. Create a feature branch: `feat/<scope>` (e.g., `feat/discovery-agent`)
2. Commit all changes using [Conventional Commits](https://www.conventionalcommits.org/):
   - `feat:` new agent / workflow / team
   - `fix:` bug fix or locator heal
   - `docs:` documentation only
   - `chore:` tooling, scripts, config
   - `test:` test automation code
3. Push the branch to GitHub.
4. **Do not auto-merge to main** — open a PR for human review.

---

## 15. Gated Roadmap Summary

```
Phase 0   → Docker + /health 200       ✅ DONE
Phase 0.5 → Site Manifesto in PgVector ✅ DONE
Phase 1   → Codebase KB indexed        ✅ DONE
Phase 2   → Gherkin workflow live      ✅ DONE
Phase 3   → Spec → Code → Green        ✅ DONE
Phase 4   → Triage + Heal loop         ✅ DONE
Phase 5   → 95% autonomous / 30 days   🔄 NEXT
```

Never implement Phase 5 work until Phase 4 gate is verified in `docs/CHECKLIST.md`.

# GitHub Copilot Instructions — Quality Autopilot
# This file ensures GitHub Copilot respects the project architecture.

## Project Context

Quality Autopilot is an Agentic Compiler for the Software Testing Life Cycle built on the Agno framework.

## Required Reading

Always consult these files before generating code:
- `AGENTS.md` — Full architecture specification (THE LAW)
- `CHECKLIST.md` — Implementation phases and current progress
- `CLAUDE.md` — Quick reference architecture overview

## Constraints

### Framework
- Use ONLY the Agno framework: `agno.agent.Agent`, `agno.team.Team`, `agno.workflow.Workflow`, `agno.os.AgentOS`
- NEVER use LangChain, CrewAI, AutoGen, or LlamaIndex

### Architecture
- Every agent has its own directory: `agents/{name}/` with agent.py, instructions.py, __init__.py, __main__.py
- Every team has its own directory: `teams/{name}/` with team.py, instructions.py, __init__.py
- Every workflow has its own directory: `workflows/{name}/` with workflow.py, instructions.py, __init__.py
- Hand-off contracts live in `contracts/` as Pydantic BaseModel classes
- Database access via `db/session.py` (PostgreSQL + PgVector only)

### Agent Parameter Order (STRICT)
Identity → Model → Data → Capabilities → Instructions → Hooks → Feature-specific → Memory → Context → Output

### Code Style
- Section headers: 75-char wide `# ---` separators
- Absolute imports only (no relative imports)
- Line length: 120 characters
- All teams use `TeamMode.coordinate`

### Testing Code Rules
- No `time.sleep()` or `waitForTimeout()`
- No CSS/XPath selectors — use `data-testid`, `role`, or `text`
- Modular POM pattern — one class per page
- No hardcoded test data

### The 9 Agents
Architect (semantic_search), Scribe (gherkin_formatter), Discovery (ui_crawler), Librarian (vector_indexing), Engineer (file_writer), Data Agent (data_factory), Detective (trace_analyzer), Medic (surgical_editor), Judge (adversarial_review)

### Quality Gate
Every artifact passes through the Agentic Judge (≥90% confidence = auto-approve, <90% = Human Review)

# CLAUDE.md — Quality Autopilot

This file provides context for AI coding agents working on this repository.
For the full specification, read [AGENTS.md](./AGENTS.md) first.

## Project Overview

Quality Autopilot — An agentic compiler for the Software Testing Life Cycle (STLC).
Built on the Agno Framework. Uses LLM reasoning to design tests and Playwright for execution.

## Architecture

```
Quality Autopilot (app/main.py)
├── Agents (9)
│   ├── Architect (agents/architect/)          # semantic_search → Execution Plan JSON
│   ├── Scribe (agents/scribe/)                # gherkin_formatter → .feature files
│   ├── Discovery (agents/discovery/)          # ui_crawler → Site Manifesto (Accessibility Tree)
│   ├── Librarian (agents/librarian/)          # vector_indexing → Up-to-date Vector KB (Git-triggered)
│   ├── Engineer (agents/engineer/)            # file_writer → GitHub PR (Look-Before-You-Leap)
│   ├── Data Agent (agents/data_agent/)        # data_factory → run_context.json
│   ├── Detective (agents/detective/)          # trace_analyzer → RCA Report
│   ├── Medic (agents/medic/)                  # surgical_editor → Healing Patch PR
│   └── Judge (agents/judge/)                  # adversarial_review → JudgeVerdict (Quality Gate)
├── Teams (4 Squads)
│   ├── Strategy (teams/strategy/)             # Architect + Scribe (coordinate)
│   ├── Context (teams/context/)               # Discovery + Librarian (coordinate)
│   ├── Engineering (teams/engineering/)        # Engineer + Data Agent (coordinate)
│   └── Operations (teams/operations/)         # Detective + Medic (coordinate)
├── Workflows (3)
│   ├── Spec to Code (workflows/spec_to_code/) # Requirement → Spec → Code → PR
│   ├── Discovery (workflows/discovery_onboard/)# AUT → Site Manifesto → KB
│   └── Triage Heal (workflows/triage_heal/)   # Failure → RCA → Patch → Verify
└── Contracts (8 Pydantic models)
    ├── RequirementContext, GherkinSpec, SiteManifesto, RunContext
    └── ExecutionResult, RCAReport, HealingPatch, JudgeVerdict

Automation Framework (automation/)
├── features/ - BDD feature files (.feature)
├── step_definitions/ - Cucumber step implementations (.ts)
├── pages/ - Playwright Page Object Models (.ts)
├── hooks/ - Test lifecycle hooks (.ts)
├── fixtures/ - Test data fixtures (.ts)
├── config/ - AUT-specific configuration
├── cucumber.conf.ts - Cucumber configuration
├── playwright.config.ts - Playwright browser config
└── tsconfig.json - TypeScript configuration
```

## Responsibility Handoff (Canonical Flow)

```
BA moves ticket → Architect → Scribe → Gherkin Judge (≥90% auto, <90% Human)
→ Data Agent → Engineer (Look-Before-You-Leap) → Code Judge (≥90% auto, <90% Human)
→ Local Green → PR submitted
CI/CD fail → Detective → Medic → Healing Judge → 3x verify → auto/Human
```

All agents share:
- PostgreSQL 16+ with PgVector for persistence
- OpenAI model (configured in `app/settings.py`)
- Chat history and context management

## Key Files

| File | Purpose |
|------|---------|
| `app/main.py` | AgentOS entry point, registers all agents, teams, workflows |
| `app/settings.py` | Shared MODEL, agent_db, AUT config |
| `db/session.py` | `get_postgres_db()` and `create_knowledge()` helpers |
| `db/url.py` | Builds database URL from environment |
| `contracts/` | Pydantic models for all agent hand-off protocols |
| `compose.yaml` | Docker Compose for full stack |

## Development Setup

```bash
# Start services
docker compose up -d --build

# Local development
python -m app.main

# Format & validate
./scripts/format.sh
./scripts/validate.sh
```

## Automation Framework Setup

```bash
# Install dependencies
cd automation
npm install

# Run tests
npm test

# Run tests with visible browser
npm run test:headed

# Run specific feature
npx cucumber-js features/login.feature --require hooks/**/*.ts --require step_definitions/**/*.ts --require-module ts-node/register
```

## Conventions

See [AGENTS.md](./AGENTS.md) for the full specification including:
- Parameter ordering (Agent, Team, Workflow)
- Section header format
- Import conventions
- File structure requirements
- Anti-patterns to avoid

## Gated Roadmap

Phase 0 → 0.5 → 1 → 2 → 3 → 4 → 5

Every phase has a gate. Do not proceed until the gate passes.
See Section XII of AGENTS.md for details.

## Environment Variables

Required:
- `OPENAI_API_KEY`

Automation Framework:
- `BASE_URL` - AUT base URL (default: https://demo.nopcommerce.com/)
- `HEADLESS` - Run tests in headless mode (default: true)
- `BROWSER` - Browser to use (default: chromium)

## Ports

- API: 8000
- Database: 5432
- Agent UI: 3000
- Playwright MCP: 8931

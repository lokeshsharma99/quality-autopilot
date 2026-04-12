# Quality Autopilot

**Agentic Compiler for the Software Testing Life Cycle (STLC).**

Quality Autopilot treats AI as a Senior SDET that reasons through requirements, writes Playwright automation, and self-heals broken tests.

## Quick Start

### Prerequisites

- [Docker Desktop](https://www.docker.com/products/docker-desktop/) (running)
- Ollama Cloud API key (or configure your own OpenAI-compatible endpoint)

### Setup

```bash
# 1. Copy environment file and configure your API keys
cp example.env .env
# Edit .env and set at minimum:
#   - OLLAMA_API_KEY=your_api_key
#   - OLLAMA_BASE_URL=http://host.docker.internal:11434 (or your Ollama Cloud endpoint)
#   - OLLAMA_MODEL=gpt-oss:120b-cloud (or your preferred model)

# 2. Start all services (includes qap-db, qap-api, qap-ui)
docker compose up -d --build

# 3. Verify the API is healthy
curl http://localhost:8000/health
# Expected response: {"status":"ok","instantiated_at":"..."}
```

### Access

| Service | URL | Purpose |
|---------|-----|---------|
| **AgentOS API** | http://localhost:8000 | FastAPI backend for agents |
| **API Docs** | http://localhost:8000/docs | Interactive API documentation |
| **Agent UI** | http://localhost:3000 | Web interface to interact with agents |
| **PostgreSQL** | localhost:5432 | Vector database (PgVector) |

## Architecture

```
Quality Autopilot
├── 9 Agents  — Architect, Scribe, Discovery, Librarian, Engineer,
│                Data Agent, Detective, Medic, Judge
├── 4 Squads  — Strategy, Context, Engineering, Operations
├── 3 Flows   — Spec-to-Code, Discovery, Triage-Heal
└── 8 Contracts — Pydantic hand-off models
```

## Current Status

**Phase 0: Infrastructure Bootstrap** ✅ Complete
- Docker Compose stack (qap-db, qap-api, qap-ui) running
- AgentOS API accessible at http://localhost:8000
- Agent UI accessible at http://localhost:3000
- PostgreSQL with PgVector configured

**Phase 0.5: AUT Onboarding (Discovery)** 🚧 In Progress
- Discovery agent created and registered
- SiteManifesto contract defined
- UI Crawler tool with curl_cffi (Cloudflare bypass) implemented
- Next: Test Discovery agent via Agent UI to crawl demo.nopcommerce.com

## AUT (Application Under Test)

Default target: [nopCommerce Demo](https://demo.nopcommerce.com/)

Configure in `.env`:
```bash
AUT_BASE_URL=https://demo.nopcommerce.com/
AUT_AUTH_USER=your_username
AUT_AUTH_PASS=your_password
```

## Documentation

| File | Purpose |
|------|---------|
| [AGENTS.md](./AGENTS.md) | Full architecture specification |
| [CHECKLIST.md](./CHECKLIST.md) | Implementation progress tracker |
| [CLAUDE.md](./CLAUDE.md) | Quick reference overview |
| [.instructions.md](./.instructions.md) | AI agent system instructions |

## Development

```bash
# View service logs
docker compose logs -f qap-api
docker compose logs -f qap-ui

# Stop all services
docker compose down

# Restart a specific service
docker compose restart qap-api

# Format & validate code
./scripts/format.sh
./scripts/validate.sh
```

## Testing the Discovery Agent

1. Open Agent UI at http://localhost:3000
2. Select the **Discovery** agent
3. Enter prompt: "Crawl https://demo.nopcommerce.com/ and generate a Site Manifesto"
4. The agent will use curl_cffi to bypass Cloudflare and extract the site structure
5. Review the generated SiteManifesto JSON output

## Troubleshooting

**Services not starting?**
```bash
# Check Docker is running
docker ps

# View logs for errors
docker compose logs
```

**Agent UI not connecting?**
- Ensure qap-api is running: `docker compose ps qap-api`
- Check API health: `curl http://localhost:8000/health`
- Verify NEXT_PUBLIC_API_URL in compose.yaml points to qap-api

## License

Proprietary. All rights reserved.

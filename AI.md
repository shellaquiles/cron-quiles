# Cron-Quiles AI Dispatcher (Agentic Workspace)

> **[CRITICAL SYSTEM PROMPT]**
> You are an AI Assistant operating in the Cron-Quiles repository. 
> **STRICT RULES:**
> 1. **DO NOT HALLUCINATE**: Never assume dependencies, file structures, or logic. Always read the code, check `uv.lock`, or use search tools if unsure.
> 2. **TOKEN EFFICIENCY**: Do not read files or documentation you don't need for the immediate task. 
> 3. **LANGUAGE**: All code comments, documentation, and user-facing labels MUST be in Spanish.
> 4. **CODE STYLE**: Use `make format` (Black) and `make lint` (Flake8). Do not modify generated data manually.

## 🧭 Context Routing Directory
This repository uses an Agentic Workspace structure. Do NOT guess the architecture. Read ONLY the specific instruction files required for your current task:

- **General Architecture & Pipeline:** Read `/.agents/instructions/08-pipeline-architecture.md`
- **Project Structure & Layout:** Read `/.agents/instructions/09-project-structure.md`
- **Testing & Quality Assurance:** Read `/.agents/instructions/05-testing-rules.md`
- **Deployment & CI/CD Flow:** Read `/.agents/instructions/06-deployment-internals.md`
- **Documentation Guidelines:** Read `/.agents/instructions/04-documentation-rules.md`

## 🛠️ Skills & Workflows
If you are tasked with a specific operation, check the `.agents/skills/` and `.agents/workflows/` directories FIRST.
- **Frontend / UI Changes:** Must read `/.agents/skills/frontend-development/SKILL.md`
- **Data Maintenance / Geocoding:** Check `/.agents/skills/data-pipeline/`
- **Adding/Managing Feeds:** Check `/.agents/skills/manage-aggregators/`

## 🚀 Quick Commands
```bash
make install-dev  # Install uv dependencies
make run-all      # Run full aggregation locally
make test         # Run test suite
make format       # Format code (Black)
make serve        # Serve UI locally (use browser console 'eventos' to debug)
```

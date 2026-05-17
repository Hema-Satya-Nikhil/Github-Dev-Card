# GitHub Dev Card Generator

This project is an agentic system that generates premium "Liquid Glass" style developer cards based on GitHub profiles.

## Architecture & Tech Stack

- **LLM:** Gemini 1.5 Flash (chosen for its high free-tier quota of 1,500 RPD).
- **Agent Orchestration:** Google Agent Development Kit (ADK).
- **Tool Protocol:** Model Context Protocol (MCP) using `FastMCP`.
- **Backend:** FastAPI (Python 3.12).
- **Frontend:** Vanilla HTML/JS/CSS with "Liquid Glass" (Apple-inspired) aesthetic.
- **Dependency Management:** `uv` (preferred) or `pip`.
- **Deployment:** Dockerized for Google Cloud Run.

## Project Structure

- `backend/`: Contains the agentic logic and API.
  - `mcp_server.py`: Defines the tools (scrape, analyze, generate, save).
  - `agent.py`: Configures the ADK Agent and its toolsets.
  - `main.py`: FastAPI application that runs the agent runner.
- `frontend/`: Contains the single-page UI.
  - `index.html`: The premium glassmorphism interface.
- `docker-compose.yml`: Orchestrates the full stack for local development.

## Strategic Conventions

- **MCP Transport:** Always use `stdio` for local tool communication between the ADK and FastMCP.
- **Tool Sequencing:** The agent follows a strict 4-step sequence: `scrape_github` -> `analyze_profile` -> `generate_card_html` -> `save_card`.
- **Frontend Variables:** The frontend uses `envsubst` to dynamically inject the `BACKEND_URL` at container runtime.

## Setup & Execution

### Local Development
1. Configure `.env` in the `backend/` folder with `GEMINI_API_KEY` and `GITHUB_TOKEN`.
2. Run `python backend/main.py`.
3. Open `frontend/index.html`.

### Docker
1. Run `docker-compose up --build`.
2. Access the UI at `http://localhost`.

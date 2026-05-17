# 🃏 GitHub Dev Card Generator

> Generate a beautiful **interactive stacked dev card** from any public GitHub profile — powered by the GitHub API, served via FastAPI, and deployed on Google Cloud Run.

**🌐 Live Demo:** [https://github-dev-card-178373694491.asia-south1.run.app](https://github-dev-card-178373694491.asia-south1.run.app)

---

## ✨ Features

- **🔍 Real GitHub Data** — scrapes live profile, repos, languages, and stats
- **🃏 Interactive Stacked Cards** — 3-panel drag-to-shuffle card (Profile → Stats → Projects)
- **🎨 Liquid Glass UI** — premium glassmorphism dark theme with per-theme accent colors
- **📱 Mobile Responsive** — swipe to shuffle on touch devices
- **⬇️ Download as PNG** — 2× retina-quality capture via html2canvas
- **🔗 Copy Card URL** — share a direct link to any generated card
- **⚡ Zero AI Quota** — profile analysis uses smart rule-based logic (no Gemini API calls)
- **🚀 Cloud Run Ready** — single container serves both frontend and API

---

## 🃏 Card Panels

Each generated card has **3 draggable panels**:

| Panel | Content |
|-------|---------|
| **1 — Profile** | Avatar · Name · Username · Developer theme badge · Vibe quote |
| **2 — Stats & Skills** | Repos / Followers / Stars · Top language pills |
| **3 — Projects** | Top 3 repos with stars · Fun fact |

**Drag left** (or swipe on mobile) to shuffle to the next panel. Click any back card to bring it forward.

---

## 🎨 Developer Themes

The card theme is automatically determined from the user's primary language and bio:

| Theme | Trigger | Accent Color |
|-------|---------|-------------|
| `Builder` | JavaScript, TypeScript, Java, Go | 🔵 Blue |
| `Researcher` | Python, Jupyter, R | 🟣 Purple |
| `Hacker` | C, C++, Rust, Shell | 🟢 Green |
| `Designer` | HTML, CSS, Vue, Swift | 🟡 Amber |
| `Open Source Hero` | Ruby, or bio mentions "oss"/"contributor" | 🌿 Green |

---

## 🏗️ Architecture

```
github-card-generator/
├── backend/
│   ├── main.py          # FastAPI app — serves API + frontend
│   ├── mcp_server.py    # Tool pipeline: scrape → analyze → generate → save
│   ├── agent.py         # ADK agent config (kept for reference)
│   └── requirements.txt
├── frontend/
│   └── index.html       # Vanilla JS/CSS — premium Liquid Glass UI
├── Dockerfile           # Single container for Cloud Run
├── .dockerignore
└── docker-compose.yml   # Local development
```

### Tool Pipeline (in `mcp_server.py`)

```
scrape_github()     →  Fetches profile, repos, languages from GitHub API
analyze_profile()   →  Rule-based vibe/theme/skills analysis (no AI quota!)
generate_card_html()→  Renders premium 3-panel stacked HTML card
save_card()         →  Saves to backend/static/cards/{username}.html
```

---

## 🚀 Quick Start — Local Development

### Prerequisites
- Python 3.12+
- A GitHub Personal Access Token (for higher API rate limits)

### 1. Clone & configure

```bash
git clone https://github.com/Hema-Satya-Nikhil/Github-Dev-Card.git
cd Github-Dev-Card

# Create your .env file
cp .env.example backend/.env
```

Edit `backend/.env`:
```env
GITHUB_TOKEN=your_github_personal_access_token
GEMINI_API_KEY=your_gemini_api_key   # Optional — not used currently
```

### 2. Install dependencies

```bash
cd backend
pip install -r requirements.txt
```

### 3. Run the server

```bash
python main.py
```

Open **http://localhost:8080** — the frontend is served directly by FastAPI.

---

## 🐳 Docker

```bash
# Build and run the full stack
docker-compose up --build

# Or manually
docker build -t github-dev-card .
docker run -p 8080:8080 \
  -e GITHUB_TOKEN=your_token \
  github-dev-card
```

---

## ☁️ Deploy to Google Cloud Run

```bash
# One-command deploy (from repo root)
gcloud run deploy github-dev-card \
  --source . \
  --region asia-south1 \
  --platform managed \
  --allow-unauthenticated \
  --port 8080 \
  --memory 512Mi \
  --set-env-vars "GITHUB_TOKEN=your_token"
```

---

## 🔌 API Reference

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/` | `GET` | Serves the frontend UI |
| `/health` | `GET` | Health check — `{"status": "healthy"}` |
| `/generate` | `POST` | Generate a card for a username |
| `/card/{username}` | `GET` | Fetch saved card HTML |
| `/static/cards/{username}.html` | `GET` | Serve the card directly |

### POST `/generate`

```json
// Request
{ "username": "torvalds" }

// Response
{
  "username": "torvalds",
  "card_url": "/static/cards/torvalds.html"
}
```

---

## 🛠️ Tech Stack

| Layer | Technology |
|-------|-----------|
| **Backend** | FastAPI · Python 3.12 · Uvicorn |
| **Data** | GitHub REST API · httpx |
| **Frontend** | Vanilla HTML · CSS · JavaScript |
| **Card Capture** | html2canvas |
| **Container** | Docker · uv |
| **Hosting** | Google Cloud Run (asia-south1) |

---

## 📄 Environment Variables

| Variable | Required | Description |
|----------|----------|-------------|
| `GITHUB_TOKEN` | Recommended | GitHub PAT for 5,000 req/hr rate limit |
| `GEMINI_API_KEY` | Optional | Not used — analysis is rule-based |

> **⚠️ Never commit your `.env` file.** It is listed in `.gitignore`.

---

## 🙌 Contributing

1. Fork the repo
2. Create a feature branch: `git checkout -b feat/my-feature`
3. Commit your changes: `git commit -m "feat: add something cool"`
4. Push and open a PR

---

## 📝 License

MIT — do whatever you want with it.

---

<div align="center">
  Made with ❤️ by <a href="https://github.com/Hema-Satya-Nikhil">Hema Satya Nikhil</a>
</div>

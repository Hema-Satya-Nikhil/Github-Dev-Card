# backend/main.py
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
import os
import uvicorn

# Import MCP tool functions directly — bypass the ADK runner to save API quota.
# The tool sequence is fixed (scrape → analyze → generate → save), so we
# don't need an AI agent to orchestrate it.
from mcp_server import scrape_github, analyze_profile, generate_card_html, save_card

from fastapi.responses import FileResponse

app = FastAPI(title="GitHub Dev Card API")

# CORS configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Paths
BASE_DIR    = os.path.dirname(__file__)
static_dir  = os.path.join(BASE_DIR, "static")
frontend_dir = os.path.join(BASE_DIR, "..", "frontend")
os.makedirs(os.path.join(static_dir, "cards"), exist_ok=True)

# Serve generated cards
app.mount("/static", StaticFiles(directory=static_dir), name="static")

# Serve frontend assets (CSS, JS, images)
if os.path.isdir(frontend_dir):
    app.mount("/frontend", StaticFiles(directory=frontend_dir), name="frontend")

@app.get("/")
async def root():
    """Serve the frontend index.html"""
    index_path = os.path.join(frontend_dir, "index.html")
    if os.path.isfile(index_path):
        return FileResponse(index_path, media_type="text/html")
    return {"message": "GitHub Dev Card Generator API is running"}

@app.get("/health")
async def health():
    return {"status": "healthy"}

class GenerateRequest(BaseModel):
    username: str

@app.post("/generate")
async def generate_card(request: GenerateRequest):
    username = request.username
    try:
        print(f"[1/4] Scraping GitHub profile for: {username}")
        github_data = await scrape_github(username)
        if "error" in github_data:
            raise HTTPException(status_code=404, detail=github_data["error"])

        print(f"[2/4] Analyzing profile with Gemini...")
        analysis = await analyze_profile(github_data)

        print(f"[3/4] Generating card HTML...")
        html = await generate_card_html(username, github_data, analysis)

        print(f"[4/4] Saving card...")
        card_url = await save_card(username, html)

        print(f"Done! Card saved at {card_url}")
        return {
            "username": username,
            "card_url": card_url
        }
    except HTTPException:
        raise
    except Exception as e:
        print(f"Error generating card: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/card/{username}")
async def get_card(username: str):
    card_path = os.path.join(static_dir, "cards", f"{username}.html")
    if os.path.exists(card_path):
        with open(card_path, "r", encoding="utf-8") as f:
            return {"html": f.read()}
    raise HTTPException(status_code=404, detail="Card not found")

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8080)

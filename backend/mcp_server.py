# backend/mcp_server.py
from mcp.server.fastmcp import FastMCP
import httpx
import os
import hashlib
from dotenv import load_dotenv

load_dotenv()

mcp = FastMCP("GithubDevCard")


@mcp.tool()
async def scrape_github(username: str) -> dict:
    """Fetch GitHub stats for a given username."""
    headers = {}
    token = os.getenv("GITHUB_TOKEN")
    if token:
        headers["Authorization"] = f"token {token}"

    async with httpx.AsyncClient(headers=headers) as httpx_client:
        # Fetch user profile
        user_res = await httpx_client.get(f"https://api.github.com/users/{username}")
        if user_res.status_code != 200:
            return {"error": f"User {username} not found"}
        user_data = user_res.json()

        # Fetch repos
        repos_res = await httpx_client.get(
            f"https://api.github.com/users/{username}/repos?sort=updated&per_page=100"
        )
        repos_data = repos_res.json() if repos_res.status_code == 200 else []

        # Sort by stars and take top 6
        top_6_repos = sorted(
            repos_data, key=lambda x: x.get("stargazers_count", 0), reverse=True
        )[:6]

        # Aggregate languages
        languages: dict = {}
        for repo in repos_data:
            lang = repo.get("language")
            if lang:
                languages[lang] = languages.get(lang, 0) + 1

        sorted_langs = sorted(languages.items(), key=lambda x: x[1], reverse=True)

        return {
            "name": user_data.get("name") or username,
            "bio": user_data.get("bio"),
            "location": user_data.get("location"),
            "avatar_url": user_data.get("avatar_url"),
            "public_repos": user_data.get("public_repos"),
            "followers": user_data.get("followers"),
            "top_repos": [
                {
                    "name": r["name"],
                    "stars": r["stargazers_count"],
                    "language": r["language"],
                    "description": r["description"],
                }
                for r in top_6_repos
            ],
            "most_used_languages": [l[0] for l in sorted_langs[:5]],
        }


@mcp.tool()
async def analyze_profile(github_data: dict) -> dict:
    """Analyze GitHub data to determine vibe, skills, and theme — no AI needed."""
    languages = github_data.get("most_used_languages", [])
    repos = github_data.get("top_repos", [])
    bio = (github_data.get("bio") or "").lower()
    followers = github_data.get("followers", 0)
    public_repos = github_data.get("public_repos", 0)
    name = github_data.get("name", "Developer")

    # Determine top skills from languages (already ranked)
    top_skills = languages[:3] if languages else ["Code", "Git", "Open Source"]

    # Determine card theme based on primary language
    primary_lang = languages[0].lower() if languages else ""
    theme_map = {
        "python": "researcher",
        "jupyter notebook": "researcher",
        "r": "researcher",
        "c": "hacker",
        "c++": "hacker",
        "c#": "builder",
        "rust": "hacker",
        "assembly": "hacker",
        "javascript": "builder",
        "typescript": "builder",
        "html": "designer",
        "css": "designer",
        "vue": "designer",
        "svelte": "designer",
        "java": "builder",
        "kotlin": "builder",
        "swift": "designer",
        "go": "builder",
        "ruby": "open-source-hero",
        "php": "builder",
        "shell": "hacker",
        "powershell": "hacker",
    }
    card_theme = theme_map.get(primary_lang, "builder")

    # Override theme if bio contains hints
    if any(w in bio for w in ["open source", "oss", "contributor", "maintainer"]):
        card_theme = "open-source-hero"
    elif any(w in bio for w in ["research", "phd", "ml", "ai", "data", "scientist"]):
        card_theme = "researcher"
    elif any(w in bio for w in ["design", "ui", "ux", "frontend", "creative"]):
        card_theme = "designer"
    elif any(w in bio for w in ["hacker", "security", "ctf", "exploit", "pentest"]):
        card_theme = "hacker"

    # Generate developer vibe sentence
    repo_count_desc = "prolific" if public_repos > 50 else "active" if public_repos > 15 else "focused"
    lang_str = " and ".join(top_skills[:2]) if top_skills else "code"
    vibe_templates = [
        f"A {repo_count_desc} {lang_str} developer who ships with purpose.",
        f"Crafting elegant solutions with {lang_str} — one commit at a time.",
        f"Building the future with {lang_str}, {public_repos} repos deep.",
        f"A passionate {lang_str} engineer with an eye for quality.",
    ]
    idx = int(hashlib.md5(name.encode()).hexdigest(), 16) % len(vibe_templates)
    developer_vibe = vibe_templates[idx]

    # Generate fun fact
    total_stars = sum(r.get("stars", 0) for r in repos)
    if total_stars > 1000:
        fun_fact = f"Their top repos have collected {total_stars:,} stars — that's real community love!"
    elif followers > 500:
        fun_fact = f"With {followers} followers, they're a recognized voice in the dev community."
    elif public_repos > 100:
        fun_fact = f"With {public_repos} public repos, they code more than most people sleep."
    elif len(languages) > 5:
        fun_fact = f"Fluent in {len(languages)} programming languages — a true polyglot!"
    else:
        fun_fact = f"Every repo tells a story, and {name}'s is just getting started."

    return {
        "developer_vibe": developer_vibe,
        "top_skills": top_skills,
        "fun_fact": fun_fact,
        "card_theme": card_theme,
    }


@mcp.tool()
async def generate_card_html(username: str, github_data: dict, analysis: dict) -> str:
    """Generate a 3-panel stacked draggable Liquid Glass dev card."""
    theme_accents = {
        "hacker":           {"accent": "#00ff88", "glow": "rgba(0,255,136,0.18)"},
        "builder":          {"accent": "#58a6ff", "glow": "rgba(88,166,255,0.18)"},
        "researcher":       {"accent": "#bf91f3", "glow": "rgba(191,145,243,0.18)"},
        "designer":         {"accent": "#f9a825", "glow": "rgba(249,168,37,0.18)"},
        "open-source-hero": {"accent": "#2da44e", "glow": "rgba(45,164,78,0.18)"},
    }
    theme  = analysis.get("card_theme", "builder")
    colors = theme_accents.get(theme, theme_accents["builder"])
    accent = colors["accent"]
    glow   = colors["glow"]

    name       = github_data.get("name", username)
    avatar     = github_data.get("avatar_url", "")
    bio        = github_data.get("bio") or ""
    pub_repos  = github_data.get("public_repos", 0)
    followers  = github_data.get("followers", 0)
    skills     = analysis.get("top_skills", [])
    vibe       = analysis.get("developer_vibe", "")
    fun        = analysis.get("fun_fact", "")
    repos      = github_data.get("top_repos", [])[:3]
    total_stars = sum(r.get("stars", 0) for r in github_data.get("top_repos", []))
    theme_label = theme.replace("-", " ").title()

    # Panel 1 – Profile
    skills_pills = "".join(
        f'<span style="display:inline-block;margin:3px;padding:4px 12px;border-radius:20px;'
        f'background:rgba(255,255,255,0.08);border:1px solid rgba(255,255,255,0.15);'
        f'color:{accent};font-size:12px;font-weight:600;">{s}</span>'
        for s in skills
    )

    # Panel 2 – Stats & Skills
    stat_row = (
        f'<div style="display:flex;justify-content:space-around;padding:16px 0;'
        f'border:1px solid rgba(255,255,255,0.08);border-radius:14px;margin-bottom:20px;">'
        f'<div style="text-align:center;"><div style="font-size:24px;font-weight:800;color:{accent};">{pub_repos}</div>'
        f'<div style="font-size:10px;color:rgba(255,255,255,0.4);text-transform:uppercase;letter-spacing:1px;margin-top:2px;">Repos</div></div>'
        f'<div style="width:1px;background:rgba(255,255,255,0.08);"></div>'
        f'<div style="text-align:center;"><div style="font-size:24px;font-weight:800;color:{accent};">{followers}</div>'
        f'<div style="font-size:10px;color:rgba(255,255,255,0.4);text-transform:uppercase;letter-spacing:1px;margin-top:2px;">Followers</div></div>'
        f'<div style="width:1px;background:rgba(255,255,255,0.08);"></div>'
        f'<div style="text-align:center;"><div style="font-size:24px;font-weight:800;color:{accent};">{total_stars}</div>'
        f'<div style="font-size:10px;color:rgba(255,255,255,0.4);text-transform:uppercase;letter-spacing:1px;margin-top:2px;">Stars</div></div>'
        f'</div>'
    )

    # Panel 3 – Projects
    repo_items = "".join(
        f'<div style="padding:10px 14px;background:rgba(255,255,255,0.04);border-radius:10px;'
        f'border:1px solid rgba(255,255,255,0.08);margin-bottom:8px;">'
        f'<div style="display:flex;justify-content:space-between;">'
        f'<span style="font-weight:600;font-size:13px;color:rgba(255,255,255,0.9);">&#128193; {r["name"]}</span>'
        f'<span style="color:{accent};font-size:12px;font-weight:700;">&#11088; {r["stars"]}</span></div>'
        f'<div style="font-size:11px;color:rgba(255,255,255,0.4);margin-top:3px;">{r.get("language") or "Code"}</div>'
        f'</div>'
        for r in repos
    )

    card_style = (
        f"position:absolute;left:0;top:0;width:100%;height:100%;border-radius:20px;"
        f"border:2px solid rgba(100,116,139,0.35);"
        f"background:rgba(15,23,42,0.45);"
        f"backdrop-filter:blur(16px);-webkit-backdrop-filter:blur(16px);"
        f"padding:28px;box-sizing:border-box;overflow:hidden;"
        f"box-shadow:0 8px 32px rgba(0,0,0,0.4);"
        f"font-family:'Inter',system-ui,sans-serif;color:#fff;"
        f"display:flex;flex-direction:column;justify-content:center;gap:12px;"
        f"will-change:transform;transition:transform 0.35s ease;"
    )

    section_label = (
        f'font-size:10px;font-weight:700;color:rgba(255,255,255,0.35);'
        f'text-transform:uppercase;letter-spacing:1.5px;margin-bottom:8px;'
    )

    return f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>{name} &mdash; Dev Card</title>
<link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;600;700;800&display=swap" rel="stylesheet">
<style>
  *, *::before, *::after {{ box-sizing: border-box; margin: 0; padding: 0; }}
  body {{
    background: radial-gradient(ellipse at 30% 20%, {glow}, transparent 60%),
                radial-gradient(ellipse at 70% 80%, {glow}, transparent 60%),
                #0d1117;
    height: 100vh; width: 100vw;
    display: flex; align-items: center; justify-content: center;
    overflow: hidden; font-family: 'Inter', system-ui, sans-serif;
  }}
  .stack-wrapper {{
    position: relative;
    width: 320px; height: 430px;
  }}
  .dev-card {{
    {card_style}
    user-select: none;
  }}
  .dev-card[data-pos="front"]  {{
    transform: rotate(-6deg) translateX(0%);
    z-index: 3; cursor: grab;
  }}
  .dev-card[data-pos="front"]:active {{ cursor: grabbing; }}
  .dev-card[data-pos="middle"] {{
    transform: rotate(0deg) translateX(33%);
    z-index: 2; cursor: default;
  }}
  .dev-card[data-pos="back"]   {{
    transform: rotate(6deg) translateX(66%);
    z-index: 1; cursor: default;
  }}
  .hint {{
    position: absolute; bottom: -32px; left: 50%;
    transform: translateX(-50%);
    font-size: 11px; color: rgba(255,255,255,0.3);
    white-space: nowrap; letter-spacing: 0.5px;
    animation: fadeHint 3s ease 1.5s forwards;
    opacity: 1;
  }}
  @keyframes fadeHint {{ 0% {{ opacity:1 }} 100% {{ opacity:0 }} }}
  .glow-dot {{
    display:inline-block; width:8px; height:8px; border-radius:50%;
    background:{accent}; margin-right:6px; box-shadow: 0 0 6px {accent};
  }}
</style>
</head>
<body>
<div style="position:relative;">
  <div class="stack-wrapper" id="stack">

    <!-- CARD 1: Profile -->
    <div class="dev-card" data-idx="0" data-pos="front">
      <div style="text-align:center;">
        <img src="{avatar}" width="88" height="88" alt="{name}"
             style="border-radius:50%;border:2.5px solid {accent};
                    box-shadow:0 0 20px {glow};display:inline-block;"/>
      </div>
      <div style="text-align:center;">
        <h2 style="font-size:20px;font-weight:800;color:#fff;margin-bottom:4px;">{name}</h2>
        <p style="font-size:13px;color:rgba(255,255,255,0.45);margin-bottom:8px;">@{username}</p>
        <span style="font-size:11px;color:{accent};font-weight:600;
                     background:rgba(255,255,255,0.07);padding:4px 12px;border-radius:20px;">
          <span class="glow-dot"></span>{theme_label}
        </span>
      </div>
      {f'<p style="font-size:13px;color:rgba(255,255,255,0.55);text-align:center;line-height:1.5;">{bio[:80]}{"…" if len(bio)>80 else ""}</p>' if bio else ""}
      <div style="font-size:13px;color:rgba(255,255,255,0.75);padding:12px 14px;
                  background:rgba(255,255,255,0.04);border-radius:12px;
                  border-left:3px solid {accent};line-height:1.6;font-style:italic;">
        &ldquo;{vibe}&rdquo;
      </div>
      <div style="text-align:center;font-size:11px;color:rgba(255,255,255,0.2);margin-top:4px;">
        1 / 3 &nbsp;&middot;&nbsp; Drag to see more &#8594;
      </div>
    </div>

    <!-- CARD 2: Stats & Skills -->
    <div class="dev-card" data-idx="1" data-pos="middle">
      <div>
        <div style="{section_label}">&#128202; Developer Stats</div>
        {stat_row}
      </div>
      <div>
        <div style="{section_label}">&#9889; Top Skills</div>
        <div style="display:flex;flex-wrap:wrap;gap:0;">{skills_pills}</div>
      </div>
      <div style="text-align:center;font-size:11px;color:rgba(255,255,255,0.2);margin-top:auto;">
        2 / 3 &nbsp;&middot;&nbsp; @{username}
      </div>
    </div>

    <!-- CARD 3: Projects & Fun Fact -->
    <div class="dev-card" data-idx="2" data-pos="back">
      <div>
        <div style="{section_label}">&#128640; Top Projects</div>
        {repo_items}
      </div>
      <div style="padding:12px 14px;background:rgba(255,255,255,0.04);
                  border-radius:12px;border:1px solid rgba(255,255,255,0.08);">
        <div style="font-size:10px;color:{accent};font-weight:700;text-transform:uppercase;
                    letter-spacing:1px;margin-bottom:5px;">&#10024; Fun Fact</div>
        <div style="font-size:12px;color:rgba(255,255,255,0.7);line-height:1.5;">{fun}</div>
      </div>
      <div style="text-align:center;font-size:10px;color:rgba(255,255,255,0.2);">
        3 / 3 &nbsp;&middot;&nbsp; Generated by <span style="color:{accent};font-weight:600;">GitHub Dev Card</span>
      </div>
    </div>

  </div>
  <div class="hint">&#8592; Swipe left to shuffle cards</div>
</div>

<script>
  const cards = Array.from(document.querySelectorAll('.dev-card'));
  const positions = ['front', 'middle', 'back'];

  function applyPositions() {{
    cards.forEach((card, i) => {{
      card.setAttribute('data-pos', positions[i]);
    }});
  }}

  function shuffle() {{
    positions.push(positions.shift());
    applyPositions();
  }}

  // Mouse drag
  let startX = 0;
  const front = () => cards.find(c => c.getAttribute('data-pos') === 'front');

  document.getElementById('stack').addEventListener('mousedown', e => {{
    if (e.target.closest('[data-pos="front"]')) startX = e.clientX;
  }});
  document.getElementById('stack').addEventListener('mouseup', e => {{
    if (startX && startX - e.clientX > 100) shuffle();
    startX = 0;
  }});

  // Touch support
  let touchStartX = 0;
  document.getElementById('stack').addEventListener('touchstart', e => {{
    touchStartX = e.touches[0].clientX;
  }}, {{passive: true}});
  document.getElementById('stack').addEventListener('touchend', e => {{
    if (touchStartX - e.changedTouches[0].clientX > 80) shuffle();
    touchStartX = 0;
  }});

  // Click on non-front cards to bring to front
  cards.forEach(card => {{
    card.addEventListener('click', () => {{
      if (card.getAttribute('data-pos') !== 'front') shuffle();
    }});
  }});
</script>
</body>
</html>"""


@mcp.tool()
async def save_card(username: str, html: str) -> str:
    """Save the generated card to a static file."""
    os.makedirs("static/cards", exist_ok=True)
    file_path = f"static/cards/{username}.html"
    with open(file_path, "w", encoding="utf-8") as f:
        f.write(html)
    return f"/static/cards/{username}.html"


if __name__ == "__main__":
    mcp.run()

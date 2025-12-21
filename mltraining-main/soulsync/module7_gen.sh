#!/data/data/com.termux/files/usr/bin/bash
# SoulSync - Module 7 Generator (README + Deploy Guides + Accessibility Checklist)
# Usage:
#   chmod +x module7_gen.sh
#   ./module7_gen.sh

set -euo pipefail

if [ ! -f "app.py" ]; then
  echo "❌ app.py not found. Run this inside your SoulSync repo folder (where app.py exists)."
  exit 1
fi

# 1) README.md
cat > README.md <<'EOT'
# ✨ SoulSync — Student-Friendly Life RPG (Streamlit + SQLite)

SoulSync is a light-themed, student-friendly (ages 13–14) life RPG web app.
Players level up Persona-style stats via daily missions, optionally unlock location-based hidden missions, opt into leaderboards, journal, and chat with a supportive digital twin called **“Your Voice.”**

---

## ✅ Features (What’s Implemented)
- **Dashboard**: Stat cards + progress bars, streak panel
- **Daily Missions**: Auto-generated; completion grants XP; streak bonuses
- **Map (Opt-in)**: Hidden missions unlock via browser geolocation (stores unlock event only)
- **Leaderboard (Opt-in)**: Global/local + weekly/all-time; gentle anti-cheat
- **Journal**: Mood + entries stored; mirrored into memory for RAG
- **Your Voice (Chat)**: RAG over journal + mission activity; moderation + disclaimer; rate limit
- **Settings**: Consents, city/region, timezone, **minimal export**, delete controls

---

## 🧰 Tech Stack
- Frontend: **Streamlit**
- Database: **SQLite + SQLAlchemy** (upgradeable to Postgres via `DATABASE_URL`)
- Maps: **Folium + streamlit-folium**
- Geolocation (opt-in): **streamlit-js-eval**
- AI:
  - Inference: Hugging Face Inference API (optional `HF_API_KEY`) (works without key via fallback)
  - Embeddings: `all-MiniLM-L6-v2` via `sentence-transformers`

---

## ⚙️ Local Setup

### 1) Create environment
```bash
python -m venv .venv
# Windows: .venv\Scripts\activate
source .venv/bin/activate
```

### 2) Install dependencies
```bash
pip install -r requirements.txt
```

### 3) (Optional) Configure environment variables
Create a `.env` file (do not commit it):

```bash
HF_API_KEY=hf_xxx
LLM_MODEL_ID=microsoft/phi-3-mini-4k-instruct
DATABASE_URL=sqlite:///phantom_life.db
```

### 4) Seed sample missions (optional)
```bash
python -m scripts.seed
```

### 5) Run the app
```bash
streamlit run app.py
```

---

## 🧪 Run Tests
```bash
pytest -q
```

---

## 🔐 Privacy Notes
- **Location**: Optional. We do **not store coordinates**—only a “hidden mission unlocked” event.
- **Leaderboard**: Optional. Only opted-in pseudonyms appear.
- **Export**: **Minimal by default** (profile, stats, missions, journal, voice memory). Chat and audit log excluded.

---

# 🚀 Deploy

## A) Streamlit Community Cloud (recommended)
1. Push your code to a **GitHub repo**
2. Go to Streamlit Community Cloud → **Create app**
3. Select repository + branch, set **Main file path = `app.py`**
4. Add secrets/keys in **Advanced settings** (recommended; don’t commit secrets in git)
5. Deploy ✅

### Secrets setup (Streamlit Cloud)
- Locally, you can use `.streamlit/secrets.toml`, but do **not** commit it.
- In Streamlit Cloud, paste secrets in the Advanced settings “Secrets” field.

Example Streamlit secrets (TOML):
```toml
HF_API_KEY="hf_xxx"
LLM_MODEL_ID="microsoft/phi-3-mini-4k-instruct"
DATABASE_URL="sqlite:///phantom_life.db"
```

---

## B) Hugging Face Spaces (Streamlit runtime)
Hugging Face supports **Streamlit Spaces**.

### Steps
1. Create a Space and choose **Streamlit** as SDK.
2. Push files to the Space repo:
   - `app.py`
   - `requirements.txt`
   - `pages/` folder
   - `soulsync/` package
   - `assets/`, `.streamlit/config.toml`, etc.
3. Add **Space Secrets** for:
   - `HF_API_KEY`
   - `LLM_MODEL_ID`
   - `DATABASE_URL` (optional; defaults to sqlite file)

### HF Space README YAML (example)
Add this YAML block at the very top of your Hugging Face Space `README.md`:
```yaml
---
title: SoulSync
emoji: ✨
colorFrom: blue
colorTo: purple
sdk: streamlit
sdk_version: "1.34.0"
app_file: app.py
pinned: false
---
```

> Note: Streamlit Spaces only allow port **8501**, so don’t override the default port.

---

## 📎 Troubleshooting
- If Your Voice replies are generic: add `HF_API_KEY`. Without it, SoulSync uses a safe fallback.
- If embeddings are slow on first run: `sentence-transformers` downloads once, then caches.
- If HF Spaces says “no application found”: check `app_file: app.py` and `requirements.txt`.

---

## ✅ Acceptance Tests (Quick QA)
- [ ] Onboarding creates profile, shows stat cards with light theme.
- [ ] Completing a mission increases stat XP; levels update correctly (base*n^2).
- [ ] Location consent unlocks hidden missions near configured spots; declining doesn’t block normal play.
- [ ] Leaderboard shows only opted-in users; opt-out removes user after refresh.
- [ ] “Your Voice” references recent journal/missions via RAG; memory is viewable/deletable.
- [ ] Export JSON includes profile, stats, missions, journal, and voice memory (minimal export).
- [ ] Toxic inputs are flagged; disclaimer visible.

---

## 📄 License
Choose a license (MIT recommended for student demos).
EOT

# 2) ACCESSIBILITY_CHECKLIST.md
cat > ACCESSIBILITY_CHECKLIST.md <<'EOT'
# ♿ SoulSync Accessibility Checklist (WCAG AA)

This checklist targets student-friendly readability and WCAG AA alignment.

---

## 1) Color Contrast (WCAG AA)
- [ ] Normal text contrast ratio ≥ **4.5:1**
- [ ] Large text (≥ 18pt or ≥ 14pt bold) contrast ratio ≥ **3:1**
- [ ] UI components (borders, icons used as controls) contrast ratio ≥ **3:1**

### Tools
- [ ] Verify contrast using a contrast checker (e.g., WebAIM Contrast Checker).

---

## 2) Typography & Readability (Student-friendly)
- [ ] Friendly font (Poppins or Nunito)
- [ ] Clear headings and short sentences
- [ ] Avoid jargon; use simple language
- [ ] Adequate line-height (1.4–1.6)

---

## 3) Keyboard Navigation
- [ ] Everything usable with keyboard: Tab / Shift+Tab
- [ ] Buttons and inputs have clear labels
- [ ] No action requires a mouse-only gesture

---

## 4) Focus & Interaction Clarity
- [ ] Visible focus indicators
- [ ] Error messages explain “what happened” and “how to fix”
- [ ] Confirm destructive actions (delete memory/account)

---

## 5) Forms & Inputs
- [ ] Inputs have descriptive labels (not only placeholders)
- [ ] Provide hints using `st.caption()` for complex inputs
- [ ] Avoid color-only meaning (use icons + text)

---

## 6) Images & Icons
- [ ] Images include alt/caption text where possible
- [ ] Emojis/icons are supported by text labels (e.g., “📚 Study”)

---

## 7) Motion & Animations
- [ ] Avoid rapid flashing
- [ ] Optional animations (balloons) are non-essential and not frequent

---

## 8) Safety Messaging (Age Appropriate)
- [ ] Your Voice includes non-clinical disclaimer
- [ ] Crisis resources visible when harmful content is detected
- [ ] Moderation blocks sexual content and harmful instructions

---

## Quick Manual Test Script (5 minutes)
1. Use Tab to move through Dashboard and Missions.
2. Complete a mission → verify success text is readable and not color-only.
3. Open Your Voice → send a normal message → check bubble readability and disclaimer.
4. Try a toxic phrase → verify it’s flagged and safe message appears.
5. Download export JSON → ensure file downloads and includes required data.
EOT

# 3) Optional HF_SPACE_README.md (for easy copy into HF Space)
cat > HF_SPACE_README.md <<'EOT'
---
title: SoulSync
emoji: ✨
colorFrom: blue
colorTo: purple
sdk: streamlit
sdk_version: "1.34.0"
app_file: app.py
pinned: false
---

# ✨ SoulSync
A student-friendly life RPG built with Streamlit.

## Quick Start
- Add secrets in Space settings:
  - `HF_API_KEY` (optional)
  - `LLM_MODEL_ID` (optional)
  - `DATABASE_URL` (optional)

> Note: Streamlit Spaces run on port 8501 by default. Do not override the port.
EOT


echo "✅ Module 7 generated successfully (README.md + ACCESSIBILITY_CHECKLIST.md + HF_SPACE_README.md)."
echo "Next:"
echo "  git status"
echo "  git add . && git commit -m \"Module 7: docs + accessibility checklist\""
echo "  git push"

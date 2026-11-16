# 🌿 Florant: AI plant identification and care assistant

Florant identifies an indoor plant from a photo and gives personalised care advice
(watering, light, tips, pet warnings) with sources.

**How it works**
1. **Identify:** the photo goes to the PlantNet API if a key is set, otherwise to Google Gemini (vision).
2. **Retrieve:** Florant looks the species up in our own hand-built care database (`data/care_db.json`).
3. **Generate (RAG):** Gemini writes personalised advice using **only** the retrieved facts, and lists the sources.
   If the AI call fails (for example the quota is used up), Florant shows the plain care sheet instead (our baseline).

> Status: **checkpoint version** (16 Nov 2026). It works end to end, with 10 species in the database.
> See [PLAN.md](PLAN.md) for what comes next.

## Setup (clean machine)

You need Python 3.10+ and a free Gemini API key from <https://aistudio.google.com/apikey>.

```bash
git clone https://github.com/aruzhanserik/final-project-AI-course.git
cd final-project-AI-course
python -m venv .venv
# Windows: .venv\Scripts\activate     macOS/Linux: source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env        # Windows: copy .env.example .env
# open .env and paste your key after GEMINI_API_KEY=
python -m app.main
```

Open <http://127.0.0.1:5000>, upload a plant photo and press **Identify & get advice**.

## Tests

```bash
python -m pytest
```

The tests replace the external APIs with fakes, so they need no API key.

## Project structure

```
app/
  main.py        Flask app and the /api/analyze endpoint
  identify.py    PlantNet / Gemini identification
  rag.py         retrieval from the care database, LLM advice, baseline lookup
  gemini.py      small Gemini REST client
  templates/, static/   the web page
data/care_db.json  care knowledge base (10 species now, about 30 planned)
tests/             pytest tests
eval/              evaluation (in progress, see eval/README.md)
agent-logs/        key sessions with the coding agent
```

## Data, APIs and libraries
- Google Gemini API (identification and advice generation): https://ai.google.dev
- Pl@ntNet identification API (optional): https://my.plantnet.org
- Care facts summarised from the University of Missouri Extension houseplant guides and the Royal Horticultural Society (RHS) growing guides.
- Libraries: Flask, requests, python-dotenv, pytest.

API keys are read from environment variables (`.env`, which git ignores). No personal user data is collected.

# Agent session 01: Checkpoint build (16 Nov 2026)

**Tool:** Claude (Anthropic) agentic coding session, model Claude Opus 5.5. It planned, wrote files,
ran the tests and fixed code in a Linux workspace.
**Goal:** a first version that works end to end, plus PLAN.md, AGENTS.md and this log, before the checkpoint deadline.
**Note:** this file is a summary of the session. The full chat transcript export is added
next to it as `01-transcript` (exported from the Claude app).

## What I asked
- Explain the final-project requirements and our proposal in simple words.
- Build the checkpoint: upload photo → species identified → AI care advice in a basic interface.
- Whether to use the Gemini API (free tier) given the limited time.

## What the agent did
1. Read the course requirements page and our proposal (Florant).
2. Explained the project and the checkpoint requirements.
3. Advised using Gemini (one free key from AI Studio for both identification and advice),
   and told me **not** to paste my API key into the chat; it goes into `.env`.
4. Tried to connect to the GitHub repo; this failed because the GitHub account was not linked,
   so the agent produced a zip to upload through the GitHub web page instead.
5. Looked up current Gemini model names, saw they change often, and chose the
   `gemini-flash-latest` alias + `GEMINI_MODEL` env variable.
6. Wrote: Flask app (`app/`), care database with 10 species, web page, 15 pytest tests with faked APIs,
   README, PLAN.md, AGENTS.md, DECISIONS.md, `.env.example`, `.gitignore`.
7. Ran the tests (15 passed) and a smoke test of the page and of the no-key error message.

8. First real run on my laptop (VS Code, Windows). Problems and fixes, in order:
   - PowerShell blocked `.venv\Scripts\activate` ("running scripts is disabled") → `Set-ExecutionPolicy -Scope CurrentUser RemoteSigned`.
   - "Read timed out (60 s)" on a phone photo → photos are shrunk in the browser, timeout 150 s, `check_gemini.py` added.
   - `gemini-flash-latest` → 503 overloaded; `gemini-2.5-flash` → 404 not available to new users
     → new default `gemini-3.5-flash-lite` plus automatic backup models. Tests: 17 passed.

## What I checked / need to check myself
- [ ] Ran the app on my laptop with my real key and a real plant photo.
- [ ] Read `app/rag.py` and `app/identify.py` so I can explain them.
- [ ] The care facts in `data/care_db.json` must still be verified against the source pages.

## Where the agent was limited or wrong
- It could not test the real Gemini call (no network and no key in its workspace). The first real test
  happens on my machine.
- Its first plan assumed a 2-person group; I am alone for now.

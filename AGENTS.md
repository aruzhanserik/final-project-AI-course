# AGENTS.md: instructions for the coding agent

You are working on **Florant**, a Flask web app that identifies houseplants from photos
and gives care advice using RAG over `data/care_db.json`. Read `PLAN.md` first.

## Rules
1. **Never put secrets in code or commits.** Keys come from environment variables
   (`GEMINI_API_KEY`, `PLANTNET_API_KEY`, `GEMINI_MODEL`) via `.env`, which is git-ignored.
2. **Keep it simple:** Python 3.10+, Flask, `requests`. No new dependency without explaining why
   and adding it to `requirements.txt` and the README.
3. **Grounding:** advice must come only from the retrieved care facts. Do not let the LLM
   invent care facts. Keep the baseline lookup working when the LLM fails.
4. **Tests:** every change to `app/` comes with a pytest test. Tests must not call real APIs;
   use `monkeypatch` fakes. Run `python -m pytest` before saying a task is done.
5. **Small steps:** make one focused change at a time, explain what you changed and why,
   and show how to run it.
6. **Care data:** never invent care facts or source URLs. If unsure, leave a TODO for a human
   to check against the University of Missouri Extension or RHS pages.
7. **Explain your code:** we must be able to explain every line at the defense, so prefer
   clear code over clever code and add short comments where the logic is not obvious.
8. Record important decisions, and any place where you (the agent) were wrong, in `DECISIONS.md`.

## Commands
- Run: `python -m app.main` → http://127.0.0.1:5000
- Test: `python -m pytest`

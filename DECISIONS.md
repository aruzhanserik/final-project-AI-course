# DECISIONS

Important decisions, with dates. Includes places where the agent was wrong and how we noticed.

## 2026-11-16: Checkpoint build

**D1. Flask + plain HTML/JS instead of a bigger framework.**
Reason: the checkpoint had to work end to end within a few hours, it runs locally with one command,
and it is small enough for us to explain every line. We can still add a richer frontend later.

**D2. Gemini as the default identifier; PlantNet optional.**
Reason: the PlantNet key was not ready yet. One Gemini key covers both identification (vision)
and advice generation. The code tries PlantNet first when `PLANTNET_API_KEY` is set, so the
PlantNet vs Gemini comparison in the evaluation needs no code change.

**D3. Call the Gemini REST API with `requests`, not the SDK.**
Reason: fewer dependencies, easy to fake in tests, and the request/response is visible in our code.

**D4. Model name is configurable (`GEMINI_MODEL` (default `gemini-3.5-flash-lite`) + automatic backup models).**
Reason: Gemini model names change every few months (several Flash versions were deprecated in 2026).
An alias plus an env variable means a model change needs no code edit.

**D5. Retrieval is a structured lookup, not vector search.**
Reason: our corpus is one record per species, and the key is the species name. Exact → synonym →
common name → genus matching is more reliable and easier to evaluate than embeddings here.
The LLM gets only the retrieved record (grounding), and the prompt forbids adding facts.

**D6. Baseline = the same record shown as a fixed care sheet (no LLM).**
It is also the fallback when the LLM call fails (for example the free quota is used up), so the app never
shows an empty page.

**D7. Care database starts at 10 species.**
The entries are summaries of general guidance. They are not yet checked line by line against the
MU Extension / RHS pages, and the sources list the guide names, not exact URLs. The agent was told
not to invent URLs. Verifying and adding the URLs is on the plan for week 2.

## Agent mistakes / corrections
- *(Add entries here as they happen: what the agent did wrong, how we noticed, what we changed.)*
- 2026-11-16: the agent's first plan assumed a group of 2 and committing straight to GitHub. The
  GitHub account was not linked, so we switched to a zip uploaded through the GitHub web page.
- 2026-11-16: **first real run failed with "Read timed out (60 s)"** when identifying a phone photo
  of a snake plant. The agent had sent full-size photos and used a 60 s timeout, and it could not test
  the real API from its workspace. Noticed on the first manual test. Fix: the browser now shrinks photos
  to max 1024 px JPEG before upload, the timeout went up to 150 s (`GEMINI_TIMEOUT`), and
  `check_gemini.py` was added to test the key and model speed separately.
- 2026-11-16: **the agent's default model choices failed on a real key.** `gemini-flash-latest`
  returned 503 (overloaded); `gemini-2.5-flash` returned 404 ("no longer available to new users").
  Noticed with `check_gemini.py`. Fix: the default is now `gemini-3.5-flash-lite` (a current, fast model),
  and `gemini.py` automatically tries backup models (`GEMINI_FALLBACK_MODELS`) on 404/429/500/503 or timeout,
  but stops at once on other errors such as a wrong key. Two tests cover this.
  Lesson: model availability depends on the account and the day; never trust one hard-coded model name.

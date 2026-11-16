# PLAN: Florant

Written before the code, from the approved proposal. Updated at each milestone.

## Goal
A beginner uploads a photo of a houseplant. Florant identifies the species and gives
personalised care advice that is grounded in a trusted care database, with sources.

## Architecture
```
photo ──► identify (PlantNet → fallback Gemini vision) ──► species name
                                                              │
                                   retrieve from data/care_db.json (exact → synonym → common name → genus)
                                                              │
                         Gemini writes advice from the retrieved facts only (RAG) ──► web page
                                  └─ if the LLM fails: baseline care-sheet lookup
```
- Backend: Python + Flask (small, easy to run locally, easy to test).
- Frontend: one HTML page + vanilla JS (no build step).
- Knowledge base: JSON file, one record per species, with sources.
- Keys only in `.env`.

## Milestones

### Checkpoint (Mon 16 Nov), done
- [x] Upload a photo → species identified (Gemini; PlantNet if key) → AI care advice on a basic page
- [x] Care database with 10 common species
- [x] Fallback to baseline lookup if the LLM fails
- [x] Tests with faked APIs
- [x] PLAN.md, AGENTS.md / CLAUDE.md, first agent log

### Week 2 (17–22 Nov)
- [ ] Get PlantNet key; compare PlantNet vs Gemini on a first 10 photos
- [ ] Expand care database to ~20 species; verify each entry against MU Extension / RHS pages and add URLs
- [ ] Start test photo set (`eval/labels.csv`), hand-verified labels

### Week 3 (23–29 Nov)
- [ ] Care database to ~30 species
- [ ] `eval/run_identification.py`: Top-1 accuracy, PlantNet vs Gemini, on 30–50 photos
- [ ] Personal plant collection saved in the browser (localStorage, no accounts)
- [ ] Responsive layout

### Week 4 (30 Nov – 6 Dec)
- [ ] `eval/run_advice.py`: generate RAG advice and baseline advice for the same plants
- [ ] Human rubric (1–5: accuracy, relevance, usefulness, supported by sources), two raters, averaged
- [ ] Results table in `eval/RESULTS.md`

### Week 5 (7–13 Dec): code freeze Sun 13 Dec, tag v1.0
- [ ] Stretch 1: AI analysis of visible problems (yellow/brown leaves)
- [ ] Stretch 2: care schedule / watering reminders
- [ ] README from scratch on a clean machine, REFLECTION.md, DECISIONS.md complete
- [ ] Backup demo video (2–3 min)

## Evaluation plan
| What | Metric | Baseline / comparison |
|---|---|---|
| Identification | Top-1 accuracy on 30–50 labelled photos | PlantNet vs Gemini |
| Care advice | 1–5 rubric (accuracy, relevance, usefulness, source support), 2 raters | RAG + LLM vs predefined care-lookup baseline |

## Team
- Member 1 (frontend/UX, collection, care database, photo set, rating): *to be assigned when the group is complete*
- Member 2 (backend, APIs, RAG, evaluation): Aruzhan
- Note: currently working alone; instructors informed, partner joining this week.

## Risks
- Free Gemini quota runs out → baseline fallback, short focused sessions, cache results in evaluation.
- Model names change → `GEMINI_MODEL` env variable (default `gemini-3.5-flash-lite`) + automatic backup models.
- Species missing from the database → clear message; genus fallback.

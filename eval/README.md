# Evaluation (in progress, after the checkpoint)

1. **Identification**: `labels.csv` with columns `photo,scientific_name` (hand-verified).
   Put photos in `eval/photos/` (git-ignored if large). Script: Top-1 accuracy for PlantNet vs Gemini.
2. **Care advice**: for each species, generate RAG advice and baseline advice. Two raters score
   each on 1–5 for accuracy, relevance, usefulness, and support by sources; we average the scores.

Results go into `eval/RESULTS.md`. See PLAN.md weeks 2–4.

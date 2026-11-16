"""Step 2 + 3: retrieve care facts for a species, then generate advice from them (RAG).

retrieve()          -> finds the species record in data/care_db.json
generate_advice()   -> Gemini writes personalised advice using ONLY the retrieved facts
baseline_advice()   -> no-AI lookup: the same facts as a fixed template (our evaluation baseline)
"""
import json
import re
from functools import lru_cache

from . import config, gemini


def _norm(text: str) -> str:
    return re.sub(r"[^a-z ]", "", (text or "").lower().replace("-", " ")).strip()


@lru_cache(maxsize=1)
def load_db(path: str = None) -> list:
    with open(path or config.CARE_DB_PATH, encoding="utf-8") as f:
        return json.load(f)["species"]


def retrieve(scientific_name: str, common_name: str = "", db: list = None) -> dict:
    """Return {"record": dict|None, "match": "exact"|"synonym"|"common"|"genus"|"none"}."""
    db = db if db is not None else load_db()
    sci = _norm(scientific_name)
    binomial = " ".join(sci.split()[:2])  # drop author names / varieties
    genus = sci.split()[0] if sci else ""

    for rec in db:
        if binomial and binomial == _norm(rec["scientific_name"]):
            return {"record": rec, "match": "exact"}
    for rec in db:
        if binomial and binomial in {_norm(s) for s in rec.get("synonyms", [])}:
            return {"record": rec, "match": "synonym"}
    com = _norm(common_name)
    if com:
        for rec in db:
            if com in {_norm(c) for c in rec.get("common_names", [])}:
                return {"record": rec, "match": "common"}
    if genus:
        for rec in db:
            names = [rec["scientific_name"]] + rec.get("synonyms", [])
            if genus in {_norm(n).split()[0] for n in names}:
                return {"record": rec, "match": "genus"}
    return {"record": None, "match": "none"}


FACT_FIELDS = ["light", "watering", "humidity_temperature", "soil_feeding", "common_problems", "toxicity"]

ADVICE_PROMPT = """You are Florant, a friendly plant-care assistant for beginners.
Write care advice for the plant below using ONLY the facts in CARE FACTS.
Do not add facts that are not in CARE FACTS. If the user's situation needs information
that is not in the facts, say so honestly.
Personalise the advice to the USER SITUATION if one is given (for example their window,
schedule or pets).

PLANT: {name}
CARE FACTS (JSON): {facts}
SOURCES: {sources}
USER SITUATION: {situation}

Answer ONLY with JSON in this exact form:
{{"summary": "1-2 sentences",
  "watering": "personalised watering advice",
  "light": "personalised light/placement advice",
  "tips": ["2-4 short extra tips"],
  "warnings": "pet safety or other warnings, or empty string",
  "sources": ["the sources you relied on, copied from SOURCES"]}}"""


def generate_advice(record: dict, situation: str = "") -> dict:
    facts = {k: record[k] for k in FACT_FIELDS if k in record}
    prompt = ADVICE_PROMPT.format(
        name=f'{record["scientific_name"]} ({", ".join(record.get("common_names", [])[:2])})',
        facts=json.dumps(facts, ensure_ascii=False),
        sources="; ".join(record.get("sources", [])),
        situation=situation.strip() or "not given",
    )
    out = gemini.generate_json(prompt)
    advice = {
        "summary": str(out.get("summary", "")),
        "watering": str(out.get("watering", "")),
        "light": str(out.get("light", "")),
        "tips": [str(t) for t in (out.get("tips") or [])][:4],
        "warnings": str(out.get("warnings", "")),
        "sources": [str(s) for s in (out.get("sources") or record.get("sources", []))],
        "method": "rag-llm",
    }
    return advice


def baseline_advice(record: dict) -> dict:
    """Predefined care lookup with no LLM (the baseline in our evaluation)."""
    return {
        "summary": f'Care sheet for {record["scientific_name"]}.',
        "watering": record.get("watering", ""),
        "light": record.get("light", ""),
        "tips": [record.get("humidity_temperature", ""), record.get("soil_feeding", ""),
                 record.get("common_problems", "")],
        "warnings": record.get("toxicity", ""),
        "sources": record.get("sources", []),
        "method": "baseline-lookup",
    }

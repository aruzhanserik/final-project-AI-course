"""Step 1: identify the plant species from a photo.

Order: PlantNet (if PLANTNET_API_KEY is set) -> Gemini vision (if GEMINI_API_KEY is set).
Both return the same dict shape:
    {"scientific_name": str, "common_name": str, "confidence": float 0-1, "provider": str}
"""
import requests

from . import config, gemini

PLANTNET_URL = "https://my-api.plantnet.org/v2/identify/all"

IDENTIFY_PROMPT = """You are a botanist. Identify the plant species in this photo.
It is most likely a common indoor houseplant.
Answer ONLY with JSON in this exact form:
{"scientific_name": "Genus species", "common_name": "most common English name", "confidence": 0.0}
confidence is your probability (0 to 1) that the species is correct.
If there is no plant in the photo, use "scientific_name": "unknown" and confidence 0."""


class IdentificationError(RuntimeError):
    pass


def identify_with_plantnet(image_bytes: bytes, filename: str = "photo.jpg") -> dict:
    resp = requests.post(
        PLANTNET_URL,
        params={"api-key": config.PLANTNET_API_KEY},
        files=[("images", (filename, image_bytes))],
        data={"organs": ["auto"]},
        timeout=60,
    )
    if resp.status_code != 200:
        raise IdentificationError(f"PlantNet error {resp.status_code}: {resp.text[:200]}")
    results = resp.json().get("results") or []
    if not results:
        raise IdentificationError("PlantNet found no match")
    best = results[0]
    species = best.get("species", {})
    commons = species.get("commonNames") or [""]
    return {
        "scientific_name": species.get("scientificNameWithoutAuthor", "unknown"),
        "common_name": commons[0],
        "confidence": float(best.get("score", 0.0)),
        "provider": "PlantNet",
    }


def identify_with_gemini(image_bytes: bytes, mime_type: str = "image/jpeg") -> dict:
    answer = gemini.generate_json(IDENTIFY_PROMPT, image_bytes=image_bytes, mime_type=mime_type)
    return normalise_gemini_answer(answer)


def normalise_gemini_answer(answer: dict) -> dict:
    try:
        conf = float(answer.get("confidence", 0.0))
    except (TypeError, ValueError):
        conf = 0.0
    return {
        "scientific_name": str(answer.get("scientific_name", "unknown")).strip() or "unknown",
        "common_name": str(answer.get("common_name", "")).strip(),
        "confidence": max(0.0, min(1.0, conf)),
        "provider": "Gemini",
    }


def identify(image_bytes: bytes, mime_type: str = "image/jpeg", filename: str = "photo.jpg") -> dict:
    errors = []
    if config.PLANTNET_API_KEY:
        try:
            return identify_with_plantnet(image_bytes, filename)
        except Exception as exc:  # fall through to Gemini
            errors.append(str(exc))
    if config.GEMINI_API_KEY:
        try:
            return identify_with_gemini(image_bytes, mime_type)
        except Exception as exc:
            errors.append(str(exc))
    if not errors:
        raise IdentificationError("No identification API key set. Put GEMINI_API_KEY in your .env file.")
    raise IdentificationError("; ".join(errors))

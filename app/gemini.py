"""Minimal Gemini REST client (generateContent). Uses `requests` only."""
import base64
import json

import requests

from . import config

API_URL = "https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent"


class GeminiError(RuntimeError):
    pass


def generate_json(prompt: str, image_bytes: bytes = None, mime_type: str = "image/jpeg",
                  api_key: str = None, model: str = None, timeout: int = None) -> dict:
    """Send a prompt (and optionally one image) and return the model's JSON answer as a dict."""
    api_key = api_key or config.GEMINI_API_KEY
    model = model or config.GEMINI_MODEL
    timeout = timeout or config.GEMINI_TIMEOUT
    if not api_key:
        raise GeminiError("GEMINI_API_KEY is not set")

    parts = [{"text": prompt}]
    if image_bytes is not None:
        parts.append({"inline_data": {"mime_type": mime_type,
                                      "data": base64.b64encode(image_bytes).decode("ascii")}})
    body = {
        "contents": [{"role": "user", "parts": parts}],
        "generationConfig": {"responseMimeType": "application/json"},
    }

    # Try the main model first, then the backup models. We move on to the next model only when
    # the problem is the model itself: busy (503), quota used up (429), retired/unknown (404),
    # or too slow (timeout). Other errors (for example a wrong key) stop immediately.
    models = [model] + [m for m in config.GEMINI_FALLBACK_MODELS if m != model]
    errors = []
    for name in models:
        try:
            resp = requests.post(API_URL.format(model=name), json=body, timeout=timeout,
                                 headers={"x-goog-api-key": api_key})
        except requests.Timeout:
            errors.append(f"{name}: timed out")
            continue
        if resp.status_code == 200:
            return parse_response(resp.json())
        errors.append(f"{name}: {resp.status_code}")
        if resp.status_code not in RETRY_NEXT_MODEL:
            raise GeminiError(f"Gemini API error {resp.status_code} ({name}): {resp.text[:300]}")
    raise GeminiError("All Gemini models failed: " + "; ".join(errors))


RETRY_NEXT_MODEL = {404, 429, 500, 503}


def parse_response(data: dict) -> dict:
    """Pull the JSON text out of a generateContent response."""
    try:
        text = "".join(p.get("text", "") for p in data["candidates"][0]["content"]["parts"])
    except (KeyError, IndexError, TypeError):
        raise GeminiError(f"Unexpected Gemini response: {str(data)[:300]}")
    text = text.strip()
    if text.startswith("```"):  # tolerate fenced output
        text = text.strip("`")
        text = text[text.find("{"):]
    try:
        return json.loads(text)
    except json.JSONDecodeError:
        raise GeminiError(f"Gemini did not return valid JSON: {text[:300]}")

"""Quick check that your Gemini key and model work.

Run:  python check_gemini.py
It prints which models your key can use and how long one tiny request takes.
"""
import time

import requests

from app import config, gemini

if not config.GEMINI_API_KEY:
    raise SystemExit("GEMINI_API_KEY is empty. Put it in the .env file.")

print("Model in use:", config.GEMINI_MODEL)

resp = requests.get("https://generativelanguage.googleapis.com/v1beta/models",
                    headers={"x-goog-api-key": config.GEMINI_API_KEY}, timeout=30)
if resp.status_code != 200:
    raise SystemExit(f"Could not list models ({resp.status_code}): {resp.text[:300]}")
flash = [m["name"].replace("models/", "") for m in resp.json().get("models", [])
         if "generateContent" in m.get("supportedGenerationMethods", []) and "flash" in m["name"]]
print("Flash models your key can use:", ", ".join(flash) or "(none)")

start = time.time()
answer = gemini.generate_json('Reply with JSON: {"ok": true}')
print(f"Test request OK in {time.time() - start:.1f} s ->", answer)

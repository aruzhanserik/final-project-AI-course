"""Tests run without any API key: external calls are replaced with fakes."""
import io

import pytest

from app import gemini, identify, rag
from app.main import create_app


# ---------- retrieval ----------
def test_retrieve_exact_match():
    out = rag.retrieve("Monstera deliciosa")
    assert out["match"] == "exact"
    assert out["record"]["id"] == "monstera-deliciosa"


def test_retrieve_ignores_author_and_case():
    out = rag.retrieve("monstera DELICIOSA Liebm.")
    assert out["record"]["id"] == "monstera-deliciosa"


def test_retrieve_synonym():
    out = rag.retrieve("Sansevieria trifasciata")
    assert out["match"] == "synonym"
    assert out["record"]["id"] == "dracaena-trifasciata"


def test_retrieve_common_name():
    out = rag.retrieve("unknown", "Peace lily")
    assert out["match"] == "common"


def test_retrieve_genus_fallback():
    out = rag.retrieve("Aloe arborescens")
    assert out["match"] == "genus"
    assert out["record"]["id"] == "aloe-vera"


def test_retrieve_no_match():
    assert rag.retrieve("Quercus robur", "English oak")["record"] is None


def test_every_record_has_required_fields():
    for rec in rag.load_db():
        for field in rag.FACT_FIELDS + ["scientific_name", "common_names", "sources"]:
            assert rec.get(field), f"{rec['id']} is missing {field}"


# ---------- baseline & generation ----------
def test_baseline_uses_db_facts():
    rec = rag.retrieve("Aloe vera")["record"]
    adv = rag.baseline_advice(rec)
    assert adv["watering"] == rec["watering"]
    assert adv["method"] == "baseline-lookup"


def test_generate_advice_sends_facts_to_llm(monkeypatch):
    captured = {}

    def fake(prompt, **kw):
        captured["prompt"] = prompt
        return {"summary": "s", "watering": "w", "light": "l", "tips": ["a", "b"],
                "warnings": "", "sources": ["RHS"]}

    monkeypatch.setattr(gemini, "generate_json", fake)
    rec = rag.retrieve("Ficus lyrata")["record"]
    adv = rag.generate_advice(rec, "I have a cat")
    assert rec["watering"] in captured["prompt"]
    assert "I have a cat" in captured["prompt"]
    assert adv["method"] == "rag-llm" and adv["watering"] == "w"


# ---------- Gemini response parsing ----------
def test_parse_gemini_response():
    data = {"candidates": [{"content": {"parts": [{"text": '{"scientific_name": "Aloe vera"}'}]}}]}
    assert gemini.parse_response(data)["scientific_name"] == "Aloe vera"


def test_parse_gemini_bad_json():
    data = {"candidates": [{"content": {"parts": [{"text": "not json"}]}}]}
    with pytest.raises(gemini.GeminiError):
        gemini.parse_response(data)


def test_normalise_confidence_is_clamped():
    out = identify.normalise_gemini_answer({"scientific_name": "X y", "confidence": 5})
    assert out["confidence"] == 1.0


# ---------- end-to-end through the web API (APIs faked) ----------
@pytest.fixture
def client():
    return create_app().test_client()


def test_analyze_end_to_end(monkeypatch, client):
    monkeypatch.setattr(identify, "identify", lambda *a, **k: {
        "scientific_name": "Epipremnum aureum", "common_name": "Pothos",
        "confidence": 0.93, "provider": "fake"})
    monkeypatch.setattr(rag, "generate_advice", lambda rec, s="": {
        "summary": "ok", "watering": "w", "light": "l", "tips": [], "warnings": "",
        "sources": rec["sources"], "method": "rag-llm"})
    resp = client.post("/api/analyze", data={"photo": (io.BytesIO(b"img"), "p.jpg")},
                       content_type="multipart/form-data")
    body = resp.get_json()
    assert resp.status_code == 200
    assert body["plant"]["scientific_name"] == "Epipremnum aureum"
    assert body["advice"]["method"] == "rag-llm"


def test_analyze_falls_back_to_baseline(monkeypatch, client):
    monkeypatch.setattr(identify, "identify", lambda *a, **k: {
        "scientific_name": "Aloe vera", "common_name": "Aloe", "confidence": 0.9, "provider": "fake"})

    def boom(*a, **k):
        raise RuntimeError("quota exceeded")

    monkeypatch.setattr(rag, "generate_advice", boom)
    resp = client.post("/api/analyze", data={"photo": (io.BytesIO(b"img"), "p.jpg")},
                       content_type="multipart/form-data")
    assert resp.get_json()["advice"]["method"] == "baseline-lookup"


def test_analyze_requires_photo(client):
    assert client.post("/api/analyze").status_code == 400


# ---------- backup models ----------
class _Resp:
    def __init__(self, code, payload=None):
        self.status_code, self._payload, self.text = code, payload, str(payload)

    def json(self):
        return self._payload


def _ok(text):
    return _Resp(200, {"candidates": [{"content": {"parts": [{"text": text}]}}]})


def test_falls_back_to_next_model_when_busy(monkeypatch):
    calls = []

    def fake_post(url, **kw):
        calls.append(url)
        return _Resp(503, "busy") if len(calls) == 1 else _ok('{"ok": true}')

    monkeypatch.setattr(gemini.requests, "post", fake_post)
    assert gemini.generate_json("hi", api_key="k", model="main") == {"ok": True}
    assert len(calls) == 2 and "main" in calls[0]


def test_wrong_key_does_not_try_other_models(monkeypatch):
    calls = []
    monkeypatch.setattr(gemini.requests, "post",
                        lambda url, **kw: calls.append(url) or _Resp(400, "API key not valid"))
    with pytest.raises(gemini.GeminiError):
        gemini.generate_json("hi", api_key="k", model="main")
    assert len(calls) == 1

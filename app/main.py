"""Florant web app: upload a photo -> identify species -> retrieve care facts -> AI care advice.

Run:  python -m app.main   then open http://127.0.0.1:5000
"""
from flask import Flask, jsonify, render_template, request

from . import config, identify, rag


def create_app() -> Flask:
    app = Flask(__name__)
    app.config["MAX_CONTENT_LENGTH"] = config.MAX_UPLOAD_MB * 1024 * 1024

    @app.get("/")
    def index():
        return render_template("index.html",
                               has_gemini=bool(config.GEMINI_API_KEY),
                               has_plantnet=bool(config.PLANTNET_API_KEY))

    @app.get("/api/species")
    def species():
        return jsonify([{"id": r["id"], "scientific_name": r["scientific_name"],
                         "common_name": r["common_names"][0]} for r in rag.load_db()])

    @app.post("/api/analyze")
    def analyze():
        photo = request.files.get("photo")
        if photo is None or photo.filename == "":
            return jsonify({"error": "Please upload a photo."}), 400
        image_bytes = photo.read()
        situation = request.form.get("situation", "")[:500]

        # 1. Identify
        try:
            ident = identify.identify(image_bytes, photo.mimetype or "image/jpeg", photo.filename)
        except identify.IdentificationError as exc:
            return jsonify({"error": f"Could not identify the plant: {exc}"}), 502

        # 2. Retrieve
        found = rag.retrieve(ident["scientific_name"], ident["common_name"])
        record = found["record"]
        result = {"identification": ident, "match": found["match"], "advice": None}
        if record is None:
            result["message"] = ("This species is not in our care database yet "
                                 "(checkpoint version has 10 common houseplants).")
            return jsonify(result)
        result["plant"] = {"scientific_name": record["scientific_name"],
                           "common_names": record["common_names"]}

        # 3. Generate (fallback to baseline lookup if the LLM call fails)
        try:
            result["advice"] = rag.generate_advice(record, situation)
        except Exception as exc:
            result["advice"] = rag.baseline_advice(record)
            result["message"] = f"AI advice unavailable ({exc}); showing the basic care sheet."
        return jsonify(result)

    return app


app = create_app()

if __name__ == "__main__":
    app.run(debug=True)

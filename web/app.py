"""Flask app: JSON API for the agent pipeline plus the built SPA.

Endpoints:
  GET  /health            liveness and configuration probe
  GET  /api/roles         the role taxonomy for the picker
  POST /api/assessment    {role_id} -> role profile and assessment questions
  POST /api/result        {role_id, answers[]} -> readiness, gaps, grounded plan

The SPA build is served from web/static when present. All request bodies are
validated and untrusted text is sanitised before it reaches the agents.
"""

from __future__ import annotations

import logging
from pathlib import Path

from flask import Flask, jsonify, request, send_from_directory

from skillforge import __version__
from skillforge.domain import list_roles, load_catalog
from skillforge.foundry_client import is_configured
from skillforge.orchestrator import Orchestrator
from skillforge.sanitize import sanitize_identifier

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(name)s %(message)s")

STATIC_DIR = Path(__file__).resolve().parent / "static"
MAX_ANSWERS = 12
MAX_ANSWER_LEN = 4000


def create_app() -> Flask:
    app = Flask(__name__, static_folder=None)
    catalog = load_catalog()
    orchestrator = Orchestrator(catalog=catalog)

    @app.get("/health")
    def health():
        return jsonify(
            {
                "status": "ok",
                "version": __version__,
                "knowledge_backend": orchestrator.backend.name,
                "model_configured": is_configured(),
                "roles": len(catalog.roles),
            }
        )

    @app.get("/api/roles")
    def roles():
        return jsonify(
            {"roles": list_roles(catalog), "knowledge_backend": orchestrator.backend.name}
        )

    @app.post("/api/assessment")
    def assessment():
        body = request.get_json(silent=True) or {}
        role_id = sanitize_identifier(body.get("role_id", ""))
        if role_id not in catalog.roles:
            return jsonify({"error": "unknown role_id"}), 400
        return jsonify(orchestrator.start_assessment(role_id))

    @app.post("/api/result")
    def result():
        body = request.get_json(silent=True) or {}
        role_id = sanitize_identifier(body.get("role_id", ""))
        if role_id not in catalog.roles:
            return jsonify({"error": "unknown role_id"}), 400

        raw_answers = body.get("answers")
        if not isinstance(raw_answers, list) or not raw_answers:
            return jsonify({"error": "answers must be a non-empty list"}), 400
        if len(raw_answers) > MAX_ANSWERS:
            return jsonify({"error": "too many answers"}), 400

        answers = []
        for item in raw_answers:
            if not isinstance(item, dict):
                continue
            answers.append(
                {
                    "competency_id": str(item.get("competency_id", ""))[:120],
                    "question": str(item.get("question", ""))[:600],
                    "answer": str(item.get("answer", ""))[:MAX_ANSWER_LEN],
                }
            )
        return jsonify(orchestrator.complete_assessment(role_id, answers))

    # Serve the built SPA. Unknown non-API paths fall back to index.html so the
    # client router can handle them. Path traversal is rejected by send_from_directory.
    @app.get("/")
    def index():
        return _serve_spa("index.html")

    @app.get("/<path:filename>")
    def spa(filename: str):
        candidate = STATIC_DIR / filename
        if candidate.is_file():
            return _serve_spa(filename)
        return _serve_spa("index.html")

    def _serve_spa(filename: str):
        if not (STATIC_DIR / "index.html").exists():
            return (
                jsonify(
                    {
                        "message": "SkillForge API is running. Build the frontend (npm run build) to serve the UI.",
                        "health": "/health",
                        "api": ["/api/roles", "/api/assessment", "/api/result"],
                    }
                ),
                200,
            )
        return send_from_directory(STATIC_DIR, filename)

    return app


app = create_app()


if __name__ == "__main__":
    import os

    port = int(os.getenv("PORT", "8000"))
    app.run(host="0.0.0.0", port=port)

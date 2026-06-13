"""Live Foundry tests. Skipped by default; run with --run-slow and real creds."""

from __future__ import annotations

import pytest

from skillforge.foundry_client import chat_json, is_configured


@pytest.mark.slow
def test_phi4_returns_valid_json():
    if not is_configured():
        pytest.skip("Foundry model not configured")
    payload = chat_json(
        'Reply with JSON only: {"ok": true}.',
        "Confirm you are reachable.",
    )
    assert isinstance(payload, dict)


@pytest.mark.slow
def test_live_assessment_uses_model():
    if not is_configured():
        pytest.skip("Foundry model not configured")
    from skillforge.orchestrator import Orchestrator

    orch = Orchestrator()
    start = orch.start_assessment("network_engineer")
    modes = {s["agent"]: s["mode"] for s in start["steps"]}
    assert modes.get("assessor") == "model"

"""Shared test configuration.

Non-slow tests must run fully offline and deterministically, so this file scrubs
the FOUNDRY_* credentials and rebuilds the settings before each such test. That
forces is_configured() to be False and every agent down its deterministic path.
Tests marked ``slow`` keep the real environment and are skipped unless
``--run-slow`` is passed.
"""

from __future__ import annotations

import pytest

import skillforge.config as config
import skillforge.foundry_client as foundry_client

_FOUNDRY_PREFIXES = ("FOUNDRY_",)


def pytest_addoption(parser):
    parser.addoption(
        "--run-slow", action="store_true", default=False, help="run slow live Foundry tests"
    )


def pytest_collection_modifyitems(config, items):  # noqa: ARG001 - pytest hook signature
    if config.getoption("--run-slow"):
        return
    skip_slow = pytest.mark.skip(reason="needs --run-slow and live Foundry credentials")
    for item in items:
        if "slow" in item.keywords:
            item.add_marker(skip_slow)


@pytest.fixture(autouse=True)
def scrub_foundry_env(request, monkeypatch):
    """Remove FOUNDRY_* and rebuild settings for every non-slow test."""
    if request.node.get_closest_marker("slow"):
        yield
        return

    for key in list(__import__("os").environ):
        if key.startswith(_FOUNDRY_PREFIXES):
            monkeypatch.delenv(key, raising=False)

    scrubbed = config.load_settings()
    monkeypatch.setattr(config, "SETTINGS", scrubbed)
    monkeypatch.setattr(foundry_client, "SETTINGS", scrubbed)
    monkeypatch.setattr(foundry_client, "_client", None)
    yield

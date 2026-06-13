"""Central configuration. Environment is loaded once, here, at import time."""

from __future__ import annotations

import os
from dataclasses import dataclass
from pathlib import Path

from dotenv import load_dotenv

load_dotenv()

PROJECT_ROOT = Path(__file__).resolve().parent.parent
DATA_DIR = PROJECT_ROOT / "data"
ROLES_PATH = DATA_DIR / "roles.json"
SEED_CORPUS_DIR = DATA_DIR / "seed_corpus"


def _clean(value: str | None) -> str:
    """Strip surrounding whitespace and quotes that sometimes leak in from .env files."""
    if value is None:
        return ""
    return value.strip().strip('"').strip("'")


@dataclass(frozen=True)
class Settings:
    # Phi-4-mini-instruct through the Foundry OpenAI-compatible endpoint.
    foundry_endpoint: str
    foundry_model_deployment: str
    foundry_api_key: str

    # Foundry IQ grounded-knowledge layer (Azure AI Search knowledge base).
    foundry_iq_project_endpoint: str
    foundry_iq_knowledge_base: str
    foundry_iq_api_key: str
    foundry_iq_search_endpoint: str
    foundry_iq_search_key: str
    foundry_iq_api_version: str

    # Which knowledge backend the retrieval interface uses.
    knowledge_backend: str

    @property
    def model_is_configured(self) -> bool:
        return bool(self.foundry_endpoint and self.foundry_api_key and self.foundry_model_deployment)

    @property
    def foundry_iq_is_configured(self) -> bool:
        return bool(self.foundry_iq_search_endpoint and self.foundry_iq_knowledge_base)


def load_settings() -> Settings:
    return Settings(
        foundry_endpoint=_clean(os.getenv("FOUNDRY_ENDPOINT")),
        foundry_model_deployment=_clean(os.getenv("FOUNDRY_MODEL_DEPLOYMENT")) or "Phi-4-mini-instruct",
        foundry_api_key=_clean(os.getenv("FOUNDRY_API_KEY")),
        foundry_iq_project_endpoint=_clean(os.getenv("FOUNDRY_IQ_PROJECT_ENDPOINT")),
        foundry_iq_knowledge_base=_clean(os.getenv("FOUNDRY_IQ_KNOWLEDGE_BASE")),
        foundry_iq_api_key=_clean(os.getenv("FOUNDRY_IQ_API_KEY")),
        foundry_iq_search_endpoint=_clean(os.getenv("FOUNDRY_IQ_SEARCH_ENDPOINT")),
        foundry_iq_search_key=_clean(os.getenv("FOUNDRY_IQ_SEARCH_KEY")),
        foundry_iq_api_version=_clean(os.getenv("FOUNDRY_IQ_API_VERSION")) or "2026-04-01",
        knowledge_backend=(_clean(os.getenv("KNOWLEDGE_BACKEND")) or "local").lower(),
    )


SETTINGS = load_settings()

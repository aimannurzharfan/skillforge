"""Grounded-knowledge layer: one retrieval interface, two backends."""

from .interface import Passage, get_backend

__all__ = ["Passage", "get_backend"]

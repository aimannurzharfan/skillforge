"""The five SkillForge agents.

Two are purely deterministic (role_profiler, readiness_tracker); two are
model-driven (assessor, learning_planner); one is a hybrid (gap_analyzer:
code computes the gaps, the model writes the narrative). Every model-driven
path has a deterministic fallback so the system works offline.
"""

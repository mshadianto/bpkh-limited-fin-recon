"""Multi-agent module for AURIX Reconciliation."""

CREWAI_AVAILABLE = False
try:
    from crewai import Agent, Task, Crew  # noqa: F401
    CREWAI_AVAILABLE = True
except ImportError:
    pass

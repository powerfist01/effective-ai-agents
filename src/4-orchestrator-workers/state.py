"""Shared state and schemas for the Orchestrator-Workers research graph.

The `ResearchState` is the single object that flows through the graph. The `sections` field
uses an `operator.add` reducer so that workers running CONCURRENTLY (via the Send API) can each
append their one section into the shared list without overwriting each other.
"""
import operator
from typing import Annotated, TypedDict

from pydantic import BaseModel, Field


class Angle(BaseModel):
    """One research angle decided by the orchestrator."""
    title: str = Field(description="Short angle title, 2-4 words, e.g. 'Ethical Concerns'")
    focus: str = Field(description="One-line guiding question telling a researcher what to find")


class AnglePlan(BaseModel):
    """Structured output of the orchestrator LLM call."""
    depth: str = Field(description="The depth actually used: 'Quick' or 'Deep'")
    angles: list[Angle] = Field(description="The distinct research angles to investigate")


class Section(BaseModel):
    """One researched section produced by a worker."""
    index: int = Field(description="1-based angle order, used to sort the final report")
    title: str
    body: str
    sources: list[str] = Field(default_factory=list)


class ResearchState(TypedDict):
    """State for the whole graph."""
    topic: str
    depth: str | None
    angles: list[Angle]
    sections: Annotated[list[Section], operator.add]  # reducer-merged from concurrent workers
    report: str


class WorkerState(TypedDict):
    """The per-Send payload a single worker invocation receives."""
    topic: str
    angle: Angle
    index: int

"""Shared state and schemas for the Evaluator-Optimizer system-design graph.

The `DesignState` is the single object that flows through the loop. Unlike the orchestrator-workers
graph (which fans out concurrent workers and needs an `operator.add` reducer), this graph is a
SEQUENTIAL loop: one generator call, then one evaluator call, repeated. So no reducers are needed —
each node simply returns the new value for the fields it owns and "last write wins".
"""
from typing import TypedDict

from pydantic import BaseModel, Field

# The five scoring dimensions, in display order. One source of truth used by the evaluator prompt,
# the deterministic stopping logic (stopping.py), and all terminal/report formatting.
DIMENSIONS = ["Scalability", "Reliability", "Simplicity", "Cost Efficiency", "Completeness"]


class Evaluation(BaseModel):
    """Structured output of ONE evaluator LLM call: a 1-10 score + a critique per dimension.

    The fields are flat (rather than a nested list) because flat schemas are the most reliable
    thing to ask an LLM for via `with_structured_output`. The `scores()`/`critiques()` helpers
    re-key them by the human-readable dimension name so the rest of the code can iterate generically.
    """
    scalability_score: int = Field(ge=1, le=10, description="How well the design handles growth, 1-10")
    scalability_critique: str = Field(description="One specific, actionable critique about scalability")
    reliability_score: int = Field(ge=1, le=10, description="Failure handling and redundancy, 1-10")
    reliability_critique: str = Field(description="One specific, actionable critique about reliability")
    simplicity_score: int = Field(ge=1, le=10, description="How clean / not over-engineered it is, 1-10")
    simplicity_critique: str = Field(description="One specific, actionable critique about simplicity")
    cost_efficiency_score: int = Field(ge=1, le=10, description="Cost-effectiveness at scale, 1-10")
    cost_efficiency_critique: str = Field(description="One specific, actionable critique about cost")
    completeness_score: int = Field(ge=1, le=10, description="Are all important aspects specified, 1-10")
    completeness_critique: str = Field(description="One specific, actionable critique about completeness")

    def scores(self) -> dict[str, int]:
        """Map each dimension name -> its score."""
        return {
            "Scalability": self.scalability_score,
            "Reliability": self.reliability_score,
            "Simplicity": self.simplicity_score,
            "Cost Efficiency": self.cost_efficiency_score,
            "Completeness": self.completeness_score,
        }

    def critiques(self) -> dict[str, str]:
        """Map each dimension name -> its critique."""
        return {
            "Scalability": self.scalability_critique,
            "Reliability": self.reliability_critique,
            "Simplicity": self.simplicity_critique,
            "Cost Efficiency": self.cost_efficiency_critique,
            "Completeness": self.completeness_critique,
        }

    def average(self) -> float:
        """Average score across all five dimensions, rounded to one decimal place."""
        values = list(self.scores().values())
        return round(sum(values) / len(values), 1)


class IterationRecord(BaseModel):
    """One pass through the loop: the design produced and the evaluation it received."""
    iteration: int
    design: str
    evaluation: Evaluation
    average: float


class DesignState(TypedDict):
    """State for the whole graph — the single object every node reads from and writes to."""
    problem: str                 # required problem statement, e.g. "Design a URL shortener like Bitly"
    constraints: str | None      # optional extra context (scale, tech stack, budget)
    iteration: int               # current iteration number (incremented by the generator)
    max_iterations: int          # hard stop after this many iterations
    threshold: int               # every dimension must score >= this to converge (default 8)
    current_design: str          # the latest design markdown produced by the generator
    history: list[IterationRecord]  # full history of designs + evaluations, fed back each loop
    best_index: int              # index into history of the highest-scoring iteration
    converged: bool              # True if we stopped because the quality threshold was met
    report: str                  # final markdown report (built by the reporter node)

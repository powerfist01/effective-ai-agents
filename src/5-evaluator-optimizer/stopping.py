"""Deterministic stopping logic for the Evaluator-Optimizer loop.

These are PLAIN PYTHON functions — NOT LLM calls. That is the whole point of the pattern: the
decision to keep refining or to stop is made by code we can read, reason about, and unit-test,
never by a model. Both the stopping-condition node (nodes/check.py) and the conditional edge
(`route` in graph.py) reuse these same helpers so the displayed status and the actual branch can
never disagree.
"""
from state import IterationRecord


def is_converged(evaluation, threshold: int) -> bool:
    """True when EVERY dimension scores >= threshold — the quality bar is met."""
    return all(score >= threshold for score in evaluation.scores().values())


def best_iteration(history: list[IterationRecord]) -> int:
    """Index of the highest-scoring iteration in history (ties resolve to the later one)."""
    best = 0
    for i, record in enumerate(history):
        if record.average >= history[best].average:
            best = i
    return best


def should_stop(state) -> tuple[bool, str]:
    """Decide whether the loop stops after the latest evaluation.

    Returns (stop, reason) where reason is one of:
      - 'converged'      → all dimensions met the threshold
      - 'max_iterations' → we ran out of iterations without converging
      - 'continue'       → keep looping (refine again)
    """
    history = state["history"]
    latest = history[-1]
    if is_converged(latest.evaluation, state["threshold"]):
        return True, "converged"
    if state["iteration"] >= state["max_iterations"]:
        return True, "max_iterations"
    return False, "continue"

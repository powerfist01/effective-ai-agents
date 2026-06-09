"""Final stage — Reporter node.

Prints the iteration-history summary to the terminal and builds the full markdown report into
state['report']. Following the repo convention (see orchestrator-workers), the report node only
BUILDS the markdown; writing the file is done by main.py so the file IO stays in one place and the
node stays easy to unit-test.
"""
from state import DIMENSIONS, DesignState
from stopping import is_converged


def _history_summary(state) -> list[str]:
    """Build the 'Iteration N -> Avg Score' lines, flagging any iteration that met the threshold."""
    lines = []
    threshold = state["threshold"]
    for record in state["history"]:
        flag = "  ✓ Threshold met!" if is_converged(record.evaluation, threshold) else ""
        lines.append(f"Iteration {record.iteration} → Avg Score: {record.average}/10{flag}")
    return lines


def _final_record(state):
    """The iteration to return as the final design.

    On convergence that is the iteration that met the bar (the last one). If we ran out of
    iterations instead, fall back to the highest-scoring iteration we ever produced.
    """
    history = state["history"]
    if state["converged"]:
        return history[-1]
    return history[state["best_index"]]


def _build_report_markdown(state) -> str:
    """Assemble the full markdown report: problem, iteration history, convergence note, design."""
    history = state["history"]
    final = _final_record(state)

    parts = [f"# System Design Proposal: {state['problem']}", ""]

    parts.append("## Problem Statement")
    parts.append(state["problem"])
    parts.append("")
    parts.append("## Constraints")
    parts.append(state["constraints"] or "None specified")
    parts.append("")

    # Convergence note.
    parts.append("## Convergence")
    if state["converged"]:
        parts.append(f"Converged on **Iteration {final.iteration}** — all dimensions scored "
                     f">= {state['threshold']}/10 (Avg {final.average}/10).")
    else:
        parts.append(f"Did NOT fully converge within {state['max_iterations']} iterations. "
                     f"Returning the highest-scoring iteration: **Iteration {final.iteration}** "
                     f"(Avg {final.average}/10).")
    parts.append("")

    # Iteration history table + per-iteration feedback.
    parts.append("## Iteration History")
    parts.append("")
    parts.append("| Iteration | " + " | ".join(DIMENSIONS) + " | Average |")
    parts.append("|" + "---|" * (len(DIMENSIONS) + 2))
    for record in history:
        scores = record.evaluation.scores()
        row = [str(record.iteration)] + [f"{scores[d]}" for d in DIMENSIONS] + [f"{record.average}"]
        parts.append("| " + " | ".join(row) + " |")
    parts.append("")

    for record in history:
        parts.append(f"### Iteration {record.iteration} — Avg {record.average}/10")
        critiques = record.evaluation.critiques()
        scores = record.evaluation.scores()
        for dim in DIMENSIONS:
            parts.append(f"- **{dim}** ({scores[dim]}/10): {critiques[dim]}")
        parts.append("")

    # The full winning design.
    parts.append(f"## Final System Design (Iteration {final.iteration} — Avg {final.average}/10)")
    parts.append("")
    parts.append(final.design)
    parts.append("")

    return "\n".join(parts)


def report(state: DesignState) -> dict:
    """Reporter node: print the history summary and build the final markdown report."""
    print(f"\n{'=' * 5} ITERATION HISTORY {'=' * 5}\n")
    for line in _history_summary(state):
        print(line)

    return {"report": _build_report_markdown(state)}

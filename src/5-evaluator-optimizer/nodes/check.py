"""Stage 3 — Stopping-condition node (DETERMINISTIC — no LLM).

This node never calls a model. It updates the best-iteration tracker and prints the loop status
after each evaluation. The actual branch — loop back to the generator vs. exit to the reporter —
is taken by the conditional edge `route` in graph.py, which reuses the SAME pure helpers in
stopping.py so the printed status and the taken branch can never disagree.
"""
from state import DesignState
from stopping import best_iteration, should_stop


def check(state: DesignState) -> dict:
    """Stopping-condition node: update the best-iteration tracker and announce the status."""
    history = state["history"]
    best = best_iteration(history)
    _stop, reason = should_stop(state)

    if reason == "converged":
        print(f"Status: Threshold met — all dimensions >= {state['threshold']}/10. Finalizing.")
        converged = True
    elif reason == "max_iterations":
        best_record = history[best]
        print(f"\n{'=' * 5} ITERATION {state['iteration']}: Maximum Iterations Reached {'=' * 5}\n")
        print("Note: Design did not fully converge to quality threshold.")
        print(f"Returning highest scoring iteration "
              f"(Iteration {best_record.iteration} — Avg: {best_record.average}/10)")
        converged = False
    else:  # 'continue'
        print("Status: Below threshold — Refining...")
        converged = False

    return {"best_index": best, "converged": converged}

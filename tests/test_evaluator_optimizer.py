import importlib.util
import sys
from pathlib import Path

import pytest

_PATTERN = Path(__file__).parent.parent / "src" / "5-evaluator-optimizer"


@pytest.fixture(autouse=True)
def _isolate_pattern_modules():
    """Make this pattern's bare module names resolve to THIS pattern, per test.

    Patterns 4 and 5 both ship modules named `state`, `graph`, `nodes`, etc. and import them by
    bare name. In a full `pytest tests/` run they would collide in `sys.modules` (and on `sys.path`
    at collection time). So instead of mutating `sys.path` at import time, we do it per-test: put
    this pattern's dir first and evict the shared names so the next `import` re-loads them from here.
    """
    if str(_PATTERN) in sys.path:
        sys.path.remove(str(_PATTERN))
    sys.path.insert(0, str(_PATTERN))
    for name in list(sys.modules):
        if name in {"state", "graph", "stopping"} or name == "nodes" or name.startswith("nodes."):
            del sys.modules[name]
    yield


def _load_main():
    """Load this pattern's main.py under a unique module name.

    A plain `import main` collides with the other patterns' main.py, which pytest may have already
    cached in sys.modules during the same run. Loading by file path under a unique name keeps the
    patterns' `main` modules isolated.
    """
    spec = importlib.util.spec_from_file_location("eo_main", _PATTERN / "main.py")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def _make_eval(score=8, **overrides):
    """Build an Evaluation with every dimension at `score`, overriding individual *_score fields."""
    from state import Evaluation
    fields = {}
    for prefix in ["scalability", "reliability", "simplicity", "cost_efficiency", "completeness"]:
        fields[f"{prefix}_score"] = overrides.get(f"{prefix}_score", score)
        fields[f"{prefix}_critique"] = f"{prefix} critique"
    return Evaluation(**fields)


def _record(iteration, score=8, **overrides):
    from state import IterationRecord
    evaluation = _make_eval(score, **overrides)
    return IterationRecord(iteration=iteration, design=f"design {iteration}",
                           evaluation=evaluation, average=evaluation.average())


# ---- state.py / Evaluation -------------------------------------------------

def test_dimensions_has_five_entries():
    from state import DIMENSIONS
    assert len(DIMENSIONS) == 5
    assert DIMENSIONS[0] == "Scalability"


def test_evaluation_scores_keyed_by_dimension():
    from state import DIMENSIONS
    ev = _make_eval(7)
    assert set(ev.scores().keys()) == set(DIMENSIONS)
    assert all(v == 7 for v in ev.scores().values())


def test_evaluation_average_rounds_to_one_decimal():
    # Scores 6,7,8,6,7 -> 34/5 = 6.8
    ev = _make_eval(scalability_score=6, reliability_score=7, simplicity_score=8,
                    cost_efficiency_score=6, completeness_score=7)
    assert ev.average() == 6.8


def test_evaluation_critiques_keyed_by_dimension():
    ev = _make_eval(9)
    assert ev.critiques()["Scalability"] == "scalability critique"


# ---- stopping.py (deterministic logic) -------------------------------------

def test_is_converged_true_when_all_meet_threshold():
    import stopping
    assert stopping.is_converged(_make_eval(8), threshold=8) is True
    assert stopping.is_converged(_make_eval(9), threshold=8) is True


def test_is_converged_false_when_any_below_threshold():
    import stopping
    ev = _make_eval(9, reliability_score=7)  # one dimension below 8
    assert stopping.is_converged(ev, threshold=8) is False


def test_best_iteration_returns_highest_average_index():
    import stopping
    history = [_record(1, 6), _record(2, 9), _record(3, 7)]
    assert stopping.best_iteration(history) == 1  # iteration 2 (index 1) has avg 9


def test_best_iteration_ties_resolve_to_later():
    import stopping
    history = [_record(1, 8), _record(2, 8)]
    assert stopping.best_iteration(history) == 1


def test_should_stop_converged():
    import stopping
    state = {"history": [_record(1, 8)], "threshold": 8, "iteration": 1, "max_iterations": 5}
    stop, reason = stopping.should_stop(state)
    assert stop is True and reason == "converged"


def test_should_stop_max_iterations():
    import stopping
    state = {"history": [_record(1, 6)], "threshold": 8, "iteration": 5, "max_iterations": 5}
    stop, reason = stopping.should_stop(state)
    assert stop is True and reason == "max_iterations"


def test_should_stop_continue():
    import stopping
    state = {"history": [_record(1, 6)], "threshold": 8, "iteration": 2, "max_iterations": 5}
    stop, reason = stopping.should_stop(state)
    assert stop is False and reason == "continue"


# ---- generator.py ----------------------------------------------------------

def test_initial_prompt_includes_problem_and_sections():
    from nodes import generator
    messages = generator._initial_prompt.format_messages(
        problem="Design a URL shortener", constraints="None", sections="SECTION LIST")
    content = messages[0].content
    assert "Design a URL shortener" in content
    assert "SECTION LIST" in content


def test_refine_prompt_includes_history_and_latest_feedback():
    from nodes import generator
    messages = generator._refine_prompt.format_messages(
        problem="P", constraints="C", sections="S",
        history="HISTORY BLOCK", latest_feedback="LATEST CRITIQUE")
    content = messages[0].content
    assert "HISTORY BLOCK" in content
    assert "LATEST CRITIQUE" in content


def test_format_history_includes_every_iteration_and_score():
    from nodes import generator
    text = generator._format_history([_record(1, 6), _record(2, 7)])
    assert "Iteration 1" in text and "Iteration 2" in text
    assert "Scalability: 6/10" in text


def test_format_latest_feedback_lists_all_dimensions():
    from nodes import generator
    from state import DIMENSIONS
    text = generator._format_latest_feedback(_record(1, 7))
    for dim in DIMENSIONS:
        assert dim in text


# ---- evaluator.py ----------------------------------------------------------

def test_evaluator_prompt_includes_problem_and_design():
    from nodes import evaluator
    messages = evaluator._prompt.format_messages(
        problem="Design X", constraints="None", design="MY DESIGN BODY")
    content = messages[0].content
    assert "Design X" in content
    assert "MY DESIGN BODY" in content


# ---- check.py / reporter.py ------------------------------------------------

def test_history_summary_flags_converged_iteration():
    from nodes import reporter
    state = {"history": [_record(1, 6), _record(2, 8)], "threshold": 8}
    lines = reporter._history_summary(state)
    assert "✓ Threshold met!" not in lines[0]
    assert "✓ Threshold met!" in lines[1]


def test_final_record_uses_last_when_converged():
    from nodes import reporter
    state = {"history": [_record(1, 9), _record(2, 8)], "converged": True, "best_index": 0}
    assert reporter._final_record(state).iteration == 2


def test_final_record_uses_best_when_not_converged():
    from nodes import reporter
    state = {"history": [_record(1, 9), _record(2, 6)], "converged": False, "best_index": 0}
    assert reporter._final_record(state).iteration == 1


def test_build_report_markdown_contains_key_sections():
    from nodes import reporter
    state = {
        "problem": "Design a URL shortener",
        "constraints": "1M users",
        "threshold": 8,
        "max_iterations": 5,
        "converged": True,
        "best_index": 0,
        "history": [_record(1, 8)],
    }
    md = reporter._build_report_markdown(state)
    assert "# System Design Proposal: Design a URL shortener" in md
    assert "## Problem Statement" in md
    assert "1M users" in md
    assert "## Iteration History" in md
    assert "## Final System Design" in md
    assert "design 1" in md  # the winning design body


def test_build_report_markdown_notes_non_convergence():
    from nodes import reporter
    state = {
        "problem": "P", "constraints": None, "threshold": 8, "max_iterations": 5,
        "converged": False, "best_index": 1,
        "history": [_record(1, 6), _record(2, 7)],
    }
    md = reporter._build_report_markdown(state)
    assert "Did NOT fully converge" in md
    assert "Iteration 2" in md  # best index 1 -> iteration 2


# ---- graph.py --------------------------------------------------------------

def test_route_loops_back_when_not_converged():
    import graph
    state = {"history": [_record(1, 6)], "threshold": 8, "iteration": 2, "max_iterations": 5}
    assert graph.route(state) == "generator"


def test_route_finishes_when_converged():
    import graph
    state = {"history": [_record(1, 8)], "threshold": 8, "iteration": 1, "max_iterations": 5}
    assert graph.route(state) == "reporter"


def test_route_finishes_at_max_iterations():
    import graph
    state = {"history": [_record(1, 6)], "threshold": 8, "iteration": 5, "max_iterations": 5}
    assert graph.route(state) == "reporter"


def test_build_graph_compiles():
    import graph
    app = graph.build_graph()
    assert app is not None


# ---- main.py ---------------------------------------------------------------

def test_slugify_basic():
    main = _load_main()
    assert main.slugify("Design a URL shortener like Bitly!") == "design-a-url-shortener-like-bitly"


def test_save_report_writes_markdown(tmp_path):
    main = _load_main()
    path = main.save_report("Design a URL shortener", "# Report\nbody", "20260603-120000",
                            out_dir=tmp_path)
    assert path.exists()
    assert path.name == "design-a-url-shortener-20260603-120000.md"
    assert path.read_text(encoding="utf-8") == "# Report\nbody"

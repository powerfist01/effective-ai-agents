"""System Design Proposal Generator — Evaluator-Optimizer pattern (LangGraph).

A generator LLM produces a system design, an evaluator LLM scores and critiques it across five
dimensions, and the generator refines it in a loop until either every dimension clears the quality
threshold or the iteration budget runs out. The loop and the deterministic stopping logic are
modelled as a LangGraph graph (see graph.py).

Usage:
    uv run python src/5-evaluator-optimizer/main.py --problem "Design a URL shortener like Bitly"
    uv run python src/5-evaluator-optimizer/main.py \\
        --problem "Design a real-time chat system like WhatsApp" \\
        --constraints "100M users, must use PostgreSQL, tight budget"
"""
import re
import sys
from datetime import datetime
from pathlib import Path

# Add project root (for config/) and this dir (for graph/nodes/state) to sys.path.
# Same bootstrap style as the other lessons' main.py.
_root = Path(__file__).parent.parent.parent
_here = Path(__file__).parent
for _p in [str(_root), str(_here)]:
    if _p not in sys.path:
        sys.path.insert(0, _p)

import argparse

from dotenv import load_dotenv

from graph import build_graph


def slugify(text: str) -> str:
    """Turn a problem statement into a filesystem-safe slug."""
    text = re.sub(r"[^\w\s-]", "", text.lower())
    return re.sub(r"[\s_]+", "-", text).strip("-")


def save_report(problem: str, report: str, timestamp: str, out_dir: Path | None = None) -> Path:
    """Write the report markdown to outputs/<slug>-<timestamp>.md and return its path."""
    out_dir = out_dir or (Path(__file__).parent / "outputs")
    out_dir.mkdir(parents=True, exist_ok=True)
    path = out_dir / f"{slugify(problem)}-{timestamp}.md"
    path.write_text(report, encoding="utf-8")
    return path


def parse_args():
    parser = argparse.ArgumentParser(
        description="System Design Proposal Generator — Evaluator-Optimizer")
    parser.add_argument("--problem", required=True,
                        help="The system to design, e.g. 'Design a URL shortener like Bitly'")
    parser.add_argument("--constraints", default=None,
                        help="Optional context: scale, tech stack, budget, etc.")
    parser.add_argument("--max-iterations", type=int, default=5,
                        help="Hard stop after this many refine loops (default 5)")
    parser.add_argument("--threshold", type=int, default=8,
                        help="Every dimension must score >= this to converge (default 8)")
    return parser.parse_args()


def main():
    load_dotenv()
    args = parse_args()

    try:
        app = build_graph()
        # Each iteration is 3 supersteps (generator, evaluator, check); give the graph enough
        # headroom so LangGraph's default recursion limit never trips before max-iterations does.
        recursion_limit = args.max_iterations * 3 + 5
        final_state = app.invoke(
            {
                "problem": args.problem,
                "constraints": args.constraints,
                "iteration": 0,
                "max_iterations": args.max_iterations,
                "threshold": args.threshold,
                "current_design": "",
                "history": [],
                "best_index": 0,
                "converged": False,
                "report": "",
            },
            config={"recursion_limit": recursion_limit},
        )

        timestamp = datetime.now().strftime("%Y%m%d-%H%M%S")
        path = save_report(args.problem, final_state["report"], timestamp)
        print(f"\nFull report saved to: {path}")

    except Exception as e:
        print(f"\nError: {e}")
        print("- Anthropic: check ANTHROPIC_API_KEY in .env")
        print("- Ollama: ensure it is running with `ollama serve`")
        sys.exit(1)


if __name__ == "__main__":
    main()

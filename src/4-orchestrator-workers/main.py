"""Research Report Generator — Orchestrator-Workers pattern (LangGraph).

Stage 1: an orchestrator LLM decides the research angles (and depth, if unspecified).
Stage 2: one worker per angle searches the web (Tavily) and drafts a section — fanned out
         dynamically with LangGraph's Send API and merged via an operator.add state reducer.
Stage 3: a synthesizer LLM weaves the sections into a cohesive report with its own insights.
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
    """Turn a topic into a filesystem-safe slug."""
    text = re.sub(r"[^\w\s-]", "", text.lower())
    return re.sub(r"[\s_]+", "-", text).strip("-")


def save_report(topic: str, report: str, timestamp: str, out_dir: Path | None = None) -> Path:
    """Write the report markdown to outputs/<slug>-<timestamp>.md and return its path."""
    out_dir = out_dir or (Path(__file__).parent / "outputs")
    out_dir.mkdir(parents=True, exist_ok=True)
    path = out_dir / f"{slugify(topic)}-{timestamp}.md"
    path.write_text(report, encoding="utf-8")
    return path


def parse_args():
    parser = argparse.ArgumentParser(
        description="Research Report Generator — Orchestrator-Workers")
    parser.add_argument("--topic", required=True, help="The research subject")
    parser.add_argument(
        "--depth", choices=["Quick", "Deep"], default=None,
        help="Quick (3-4 angles) or Deep (6-8). Omit to let the orchestrator decide.")
    return parser.parse_args()


def main():
    load_dotenv()
    args = parse_args()

    try:
        app = build_graph()
        final_state = app.invoke({
            "topic": args.topic,
            "depth": args.depth,
            "angles": [],
            "sections": [],
            "report": "",
        })

        report = final_state["report"]

        # Terminal summary: print the first lines of the report as a preview.
        print(f"\n{'=' * 5} REPORT SUMMARY {'=' * 5}\n")
        preview = "\n".join(report.splitlines()[:15])
        print(preview)
        print("\n... (full report saved to file) ...")

        timestamp = datetime.now().strftime("%Y%m%d-%H%M%S")
        path = save_report(args.topic, report, timestamp)
        print(f"\nReport saved to: {path}")

    except Exception as e:
        print(f"\nError: {e}")
        print("- Tavily: ensure TAVILY_API_KEY is set in .env (https://tavily.com)")
        print("- Anthropic: check ANTHROPIC_API_KEY in .env")
        print("- Ollama: ensure it is running with `ollama serve`")
        sys.exit(1)


if __name__ == "__main__":
    main()

"""Product Review Analyzer — Parallelization (Sectioning) pattern.

Stage 1: fetch real reviews via Tavily.
Stage 2: run four independent analyzers CONCURRENTLY with asyncio.gather.
Stage 3: deterministically aggregate into a markdown report and save it.
"""
import sys
from datetime import datetime
from pathlib import Path

# Add project root (for config/) and this dir (for fetcher/analyzers/aggregator) to sys.path.
# Same bootstrap as src/2-routing/main.py.
_root = Path(__file__).parent.parent.parent.parent
_here = Path(__file__).parent
for _p in [str(_root), str(_here)]:
    if _p not in sys.path:
        sys.path.insert(0, _p)

import argparse
import asyncio

from dotenv import load_dotenv

import aggregator
from analyzers import audience, cons, pros, sentiment
from config.llm import get_llm
from fetcher import fetch_reviews


def parse_args():
    parser = argparse.ArgumentParser(description="Product Review Analyzer — Sectioning Pattern")
    parser.add_argument("--product", required=True, help="Product name to analyze reviews for")
    return parser.parse_args()


async def _timed(label: str, coro, on_done):
    """Await one analyzer coroutine, then print a completion line.

    Completion lines print as each task finishes — because the tasks run concurrently they
    interleave out of order, making the parallelism visually obvious.
    """
    result = await coro
    print(on_done(result), flush=True)
    return result


async def analyze(corpus: str, llm):
    """Stage 2 — run all four analyzers at the same time."""
    print(f"\n{'=' * 5} STEP 2: Running Parallel Analysis {'=' * 5}\n")

    sentiment_res, pros_res, cons_res, audience_res = await asyncio.gather(
        _timed("Sentiment", sentiment.run(corpus, llm),
               lambda r: f"[Sentiment] Complete: {r.verdict}"),
        _timed("Pros", pros.run(corpus, llm), lambda r: "[Pros] Complete"),
        _timed("Cons", cons.run(corpus, llm), lambda r: "[Cons] Complete"),
        _timed("Target Audience", audience.run(corpus, llm),
               lambda r: "[Target Audience] Complete"),
    )
    return sentiment_res, pros_res, cons_res, audience_res


async def main():
    load_dotenv()
    args = parse_args()

    try:
        # Stage 1 — fetch
        print(f"\n{'=' * 5} STEP 1: Fetching Reviews for {args.product} {'=' * 5}\n")
        corpus, count = fetch_reviews(args.product)
        print(f"Found {count} reviews from various sources...")

        llm = get_llm()

        # Stage 2 — parallel analysis
        sentiment_res, pros_res, cons_res, audience_res = await analyze(corpus, llm)

        # Stage 3 — aggregate
        report = aggregator.build_report(
            product=args.product,
            sentiment=sentiment_res.verdict,
            sentiment_reason=sentiment_res.reason,
            pros=pros_res,
            cons=cons_res,
            audience=audience_res,
        )
        print(f"\n{'=' * 5} STEP 3: Aggregated Report {'=' * 5}\n")
        print(report)

        timestamp = datetime.now().strftime("%Y%m%d-%H%M%S")
        path = aggregator.save_report(args.product, report, timestamp)
        print(f"\nReport saved to: {path}")

    except Exception as e:
        print(f"\nError: {e}")
        print("- Tavily: ensure TAVILY_API_KEY is set in .env (https://tavily.com)")
        print("- Anthropic: check ANTHROPIC_API_KEY in .env")
        print("- Ollama: ensure it is running with `ollama serve`")
        sys.exit(1)


if __name__ == "__main__":
    asyncio.run(main())

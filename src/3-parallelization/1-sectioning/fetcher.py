"""Stage 1 — fetch real product reviews from the web via Tavily (through LangChain)."""
import os

from langchain_tavily import TavilySearch


def fetch_reviews(product: str, max_results: int = 8) -> tuple[str, int]:
    """Search the web for reviews of `product`.

    Returns (corpus, count): a single concatenated string of review snippets and how many
    results were used. Raises RuntimeError with a clear message if TAVILY_API_KEY is missing
    or no results come back.
    """
    if not os.getenv("TAVILY_API_KEY"):
        raise RuntimeError(
            "TAVILY_API_KEY is not set. Add it to your .env (get a free key at https://tavily.com)."
        )

    search = TavilySearch(max_results=max_results)
    response = search.invoke({"query": f"{product} reviews"})

    # TavilySearch returns a dict with a "results" list of {title, url, content, ...}.
    results = response.get("results", []) if isinstance(response, dict) else []
    if not results:
        raise RuntimeError(f"No reviews found for '{product}'. Try a more specific product name.")

    # Build a readable corpus: each review snippet labeled with its source.
    blocks = []
    for i, r in enumerate(results, start=1):
        title = r.get("title", "Untitled")
        content = r.get("content", "").strip()
        url = r.get("url", "")
        blocks.append(f"[Review {i}] {title} ({url})\n{content}")

    corpus = "\n\n".join(blocks)
    return corpus, len(results)

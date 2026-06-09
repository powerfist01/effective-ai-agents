"""Stage 2 — Worker node.

One worker invocation handles ONE research angle: it searches the web with Tavily for that angle's
focus question, then asks the LLM to write a structured markdown section from the results. It
returns its section in a list so the `operator.add` reducer appends it to shared state.

Workers are spawned dynamically by `graph.route_to_workers` (one Send per angle) and run
concurrently, so the "[Angle N: ...] Complete" lines may print out of order.
"""
import os

from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import ChatPromptTemplate
from langchain_tavily import TavilySearch

from config.llm import get_llm
from state import Angle, Section, WorkerState


def _build_query(topic: str, angle: Angle) -> str:
    """Build a focused search query from the topic and the angle's guiding question."""
    return f"{topic}: {angle.focus}"


def _search(query: str, max_results: int = 5) -> tuple[str, list[str]]:
    """Run Tavily for `query`; return (corpus, sources). Raises if the key is missing."""
    if not os.getenv("TAVILY_API_KEY"):
        raise RuntimeError(
            "TAVILY_API_KEY is not set. Add it to your .env (free key at https://tavily.com)."
        )
    response = TavilySearch(max_results=max_results).invoke({"query": query})
    results = response.get("results", []) if isinstance(response, dict) else []
    if not results:
        # No hits — fail loudly rather than asking the LLM to write a section from nothing
        # (which invites hallucination). Mirrors fetcher.py in the sectioning pattern.
        raise RuntimeError(f"No search results for query: '{query}'. Try a broader topic.")

    blocks, sources = [], []
    for i, r in enumerate(results, 1):
        title = r.get("title", "Untitled")
        content = r.get("content", "").strip()
        url = r.get("url", "")
        blocks.append(f"[Source {i}] {title} ({url})\n{content}")
        if url:
            sources.append(url)
    return "\n\n".join(blocks), sources


_prompt = ChatPromptTemplate.from_messages([
    ("human", """You are a research analyst writing ONE section of a larger report.

Topic: {topic}
Section angle: {title}
Focus question: {focus}

Using ONLY the search results below, write a clear, well-structured section in markdown
(2-4 short paragraphs or bullet points). Be factual and do not invent sources.

Search results:
{corpus}"""),
])


def research(state: WorkerState) -> dict:
    """Worker node: one angle -> one Section appended to state['sections']."""
    angle = state["angle"]
    topic = state["topic"]
    index = state["index"]

    corpus, sources = _search(_build_query(topic, angle))

    chain = _prompt | get_llm() | StrOutputParser()
    body = chain.invoke({
        "topic": topic,
        "title": angle.title,
        "focus": angle.focus,
        "corpus": corpus,
    })

    print(f"[Angle {index}: {angle.title}] Complete", flush=True)

    section = Section(index=index, title=angle.title, body=body.strip(), sources=sources)
    return {"sections": [section]}

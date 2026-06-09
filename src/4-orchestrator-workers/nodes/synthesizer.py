"""Stage 3 — Synthesizer node.

Reads ALL worker sections and makes one LLM call that produces a cohesive report — not a raw
concatenation. It adds a title, an introduction, smooth transitions, and its own
"Conclusions and Insights" section synthesizing across every angle.
"""
from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import ChatPromptTemplate

from config.llm import get_llm
from state import ResearchState, Section


def _format_sections(sections: list[Section]) -> str:
    """Render the worker sections in angle order for the synthesis prompt."""
    ordered = sorted(sections, key=lambda s: s.index)
    return "\n\n".join(f"### {s.title}\n{s.body}" for s in ordered)


_prompt = ChatPromptTemplate.from_messages([
    ("human", """You are the lead researcher writing the FINAL report on: {topic}

Below are sections drafted by your research team, one per angle. Weave them into a single
cohesive markdown report. Do NOT just concatenate them. Your report must include:
- a top-level title (# ) and an introduction that frames the topic
- each angle as its own "## " section, using the drafted content but improving flow
- a final "## Conclusions and Insights" section with YOUR OWN synthesis across all angles.

Drafted sections:
{sections}"""),
])


def synthesize(state: ResearchState) -> dict:
    """Synthesizer node: all sections -> final report string in state['report']."""
    topic = state["topic"]
    sections = state["sections"]

    print(f"\n{'=' * 5} STEP 3: Synthesizing Research Report {'=' * 5}\n")
    print(f"Combining findings from {len(sections)} research angles...")
    print("Adding conclusions and insights...")

    chain = _prompt | get_llm() | StrOutputParser()
    report = chain.invoke({
        "topic": topic,
        "sections": _format_sections(sections),
    })

    print("Report Complete!")
    return {"report": report.strip()}

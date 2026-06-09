"""Stage 1 — Orchestrator node.

Reads the topic (and optional depth) and makes ONE structured LLM call that decides the research
angles. If depth is not given, the LLM also decides Quick (3-4 angles) vs Deep (6-8). Prints the
plan clearly so it is obvious in the terminal how the orchestrator decided.
"""
from langchain_core.prompts import ChatPromptTemplate

from config.llm import get_llm
from state import AnglePlan, ResearchState


def _depth_instructions(depth):
    """Return guidance telling the LLM how many angles to produce for the chosen depth."""
    if depth == "Quick":
        return "The user wants a QUICK report: produce 3-4 focused angles. Set depth to 'Quick'."
    if depth == "Deep":
        return "The user wants a DEEP report: produce 6-8 thorough angles. Set depth to 'Deep'."
    return (
        "The user did NOT specify a depth. YOU decide: choose 'Quick' (3-4 angles) for a narrow "
        "topic, or 'Deep' (6-8 angles) for a broad one, and set the 'depth' field accordingly."
    )


_prompt = ChatPromptTemplate.from_messages([
    ("human", """You are a research orchestrator. Break the topic into distinct research angles.

Topic: {topic}

{depth_instructions}

Each angle needs:
- title: a short label (2-4 words)
- focus: a one-line guiding question that tells a researcher exactly what to look for.

The angles must be DISTINCT and together give well-rounded coverage of the topic."""),
])


def orchestrate(state: ResearchState) -> dict:
    """Orchestrator node: one structured LLM call -> chosen depth + list of angles."""
    topic = state["topic"]
    depth = state.get("depth")

    llm = get_llm().with_structured_output(AnglePlan)
    plan: AnglePlan = (_prompt | llm).invoke({
        "topic": topic,
        "depth_instructions": _depth_instructions(depth),
    })

    print(f"\n{'=' * 5} STEP 1: Orchestrator Analyzing Topic {'=' * 5}\n")
    print(f"Topic: {topic}")
    print(f"Depth: {plan.depth}")
    print("Decided Research Angles:")
    for i, angle in enumerate(plan.angles, 1):
        print(f"  {i}. {angle.title}")

    print(f"\n{'=' * 5} STEP 2: Workers Researching {'=' * 5}\n")

    return {"depth": plan.depth, "angles": plan.angles}

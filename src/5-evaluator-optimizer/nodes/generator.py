"""Stage 1 — Generator node.

On the FIRST pass it writes an initial system design from the problem + constraints. On every
later pass it REFINES the design: it receives the original problem, the full history of previous
designs and their feedback, and the latest critique, and must address each critique specifically.

Feeding the full history (not just the last critique) is deliberate — it lets the generator see how
the design has evolved and avoid re-introducing problems that earlier iterations already fixed.
"""
from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import ChatPromptTemplate

from config.llm import get_llm
from state import DIMENSIONS, DesignState

# The required structure every design must cover. Shared by the initial and refine prompts.
_DESIGN_SECTIONS = """Your design MUST cover these sections, each as a markdown heading:
1. **Requirements** — functional and non-functional
2. **High Level Architecture** — the components and how they interact
3. **Database Design** — schema and storage choices
4. **Scalability** — how it handles growth
5. **Reliability** — failure handling and redundancy
6. **Trade-offs** — what you chose and why"""

# First iteration: design from scratch.
_initial_prompt = ChatPromptTemplate.from_messages([
    ("human", """You are a senior systems architect. Produce a complete system design proposal.

Problem: {problem}
Constraints: {constraints}

{sections}

Be concrete and well-structured. Output markdown only — no preamble."""),
])

# Later iterations: refine using the full history and the latest critique.
_refine_prompt = ChatPromptTemplate.from_messages([
    ("human", """You are a senior systems architect REFINING a system design across iterations.

Problem: {problem}
Constraints: {constraints}

{sections}

FULL history of previous iterations and the evaluator's feedback:
{history}

The MOST RECENT evaluation raised these specific critiques to fix now:
{latest_feedback}

Produce an IMPROVED, COMPLETE system design that specifically addresses EACH critique above.
Keep what already scored well; fix what was criticized. Output markdown only — no preamble."""),
])


def _format_history(history) -> str:
    """Render every past iteration's scores + critiques as text for the refine prompt."""
    blocks = []
    for record in history:
        scores = record.evaluation.scores()
        critiques = record.evaluation.critiques()
        lines = [f"--- Iteration {record.iteration} (Avg {record.average}/10) ---"]
        for dim in DIMENSIONS:
            lines.append(f"{dim}: {scores[dim]}/10 — {critiques[dim]}")
        blocks.append("\n".join(lines))
    return "\n\n".join(blocks)


def _format_latest_feedback(record) -> str:
    """Render just the latest iteration's critiques as a focused to-do list for the generator."""
    scores = record.evaluation.scores()
    critiques = record.evaluation.critiques()
    return "\n".join(f"- {dim} ({scores[dim]}/10): {critiques[dim]}" for dim in DIMENSIONS)


def generate(state: DesignState) -> dict:
    """Generator node: produce the initial design, or refine it from the full feedback history."""
    problem = state["problem"]
    constraints = state["constraints"] or "None specified"
    history = state["history"]
    iteration = state["iteration"] + 1  # this pass's iteration number

    if not history:
        print(f"\n{'=' * 5} ITERATION {iteration}: Generating System Design {'=' * 5}\n")
        print(f"Problem: {problem}")
        print("Generating initial proposal...")
        chain = _initial_prompt | get_llm() | StrOutputParser()
        design = chain.invoke({
            "problem": problem,
            "constraints": constraints,
            "sections": _DESIGN_SECTIONS,
        })
    else:
        print(f"\n{'=' * 5} ITERATION {iteration}: Refining System Design {'=' * 5}\n")
        print(f"Problem: {problem}")
        print(f"Refining based on Iteration {iteration - 1} feedback (Avg {history[-1].average}/10)...")
        chain = _refine_prompt | get_llm() | StrOutputParser()
        design = chain.invoke({
            "problem": problem,
            "constraints": constraints,
            "sections": _DESIGN_SECTIONS,
            "history": _format_history(history),
            "latest_feedback": _format_latest_feedback(history[-1]),
        })

    return {"current_design": design.strip(), "iteration": iteration}

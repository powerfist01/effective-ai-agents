"""Stage 2 — Evaluator node.

Reads the latest design and makes ONE structured LLM call that scores it 1-10 on each of the five
dimensions and gives one specific critique per dimension. It prints the scorecard with aligned
columns so it is visually obvious how each iteration compares, then appends an `IterationRecord` to
the shared history. The scoring is the model's job; the *decision* about what to do with the scores
is NOT made here — that is deterministic code in the stopping-condition node.
"""
from langchain_core.prompts import ChatPromptTemplate

from config.llm import get_llm
from state import DIMENSIONS, DesignState, Evaluation, IterationRecord

# Column width so "Scalability:" through "Cost Efficiency:" all line up in the terminal.
_LABEL_WIDTH = max(len(d) for d in DIMENSIONS) + 1  # +1 for the trailing colon

_prompt = ChatPromptTemplate.from_messages([
    ("human", """You are a strict principal engineer reviewing a system design proposal.

Problem: {problem}
Constraints: {constraints}

Design to evaluate:
{design}

Score the design from 1 to 10 on EACH dimension below, and give ONE specific, actionable
critique per dimension (what to improve — even a high score still gets a critique):
- Scalability — does it handle growth (caching, sharding, load balancing)?
- Reliability — failure handling, redundancy, no single points of failure?
- Simplicity — clean and not over-engineered for the stated problem?
- Cost Efficiency — cost-effective at the expected scale?
- Completeness — are all important aspects (API, data model, edge cases) specified?

Be honest and critical. Reserve 9-10 for genuinely excellent dimensions."""),
])


def evaluate(state: DesignState) -> dict:
    """Evaluator node: one structured LLM call -> scores + critiques, appended to history."""
    iteration = state["iteration"]
    print(f"\n{'=' * 5} ITERATION {iteration}: Evaluating Design {'=' * 5}\n")

    llm = get_llm().with_structured_output(Evaluation)
    evaluation: Evaluation = (_prompt | llm).invoke({
        "problem": state["problem"],
        "constraints": state["constraints"] or "None specified",
        "design": state["current_design"],
    })

    scores = evaluation.scores()
    critiques = evaluation.critiques()
    for dim in DIMENSIONS:
        label = f"{dim}:"
        print(f"{label:<{_LABEL_WIDTH}} {scores[dim]}/10 - {critiques[dim]}")
    average = evaluation.average()
    print(f"{'Average Score:':<{_LABEL_WIDTH}} {average}/10")

    record = IterationRecord(
        iteration=iteration,
        design=state["current_design"],
        evaluation=evaluation,
        average=average,
    )
    # Sequential loop, no reducer: return the full updated history (last write wins).
    return {"history": state["history"] + [record]}

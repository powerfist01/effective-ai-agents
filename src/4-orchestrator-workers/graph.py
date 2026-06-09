"""LangGraph wiring for the Orchestrator-Workers research pipeline.

    START -> orchestrator --(conditional edge: one Send per angle)--> worker (xN concurrent)
                                                                          |
                                                                          v
                                                                     synthesizer -> END

`route_to_workers` is the heart of the pattern: the NUMBER of workers is decided at runtime by the
orchestrator, and the Send API fans out exactly that many worker invocations. This dynamic
topology is what LangGraph gives us over a static LangChain chain.
"""
from langgraph.graph import END, START, StateGraph
from langgraph.types import Send

from nodes.orchestrator import orchestrate
from nodes.synthesizer import synthesize
from nodes.worker import research
from state import ResearchState


def route_to_workers(state: ResearchState) -> list[Send]:
    """Conditional edge: fan out ONE worker per angle via the Send API (dynamic, not hardcoded)."""
    return [
        Send("worker", {"topic": state["topic"], "angle": angle, "index": i})
        for i, angle in enumerate(state["angles"], 1)
    ]


def build_graph():
    """Build and compile the research graph."""
    graph = StateGraph(ResearchState)
    graph.add_node("orchestrator", orchestrate)
    graph.add_node("worker", research)
    graph.add_node("synthesizer", synthesize)

    graph.add_edge(START, "orchestrator")
    graph.add_conditional_edges("orchestrator", route_to_workers, ["worker"])
    graph.add_edge("worker", "synthesizer")
    graph.add_edge("synthesizer", END)

    return graph.compile()

"""LangGraph wiring for the Evaluator-Optimizer loop.

   START -> generator -> evaluator -> check --(conditional edge: route)--+
               ^                                                          |
               |                                                          |
               +------------------ "generator" (loop back) --------------+
                                                                          |
                                          "reporter" (stop) --------------+--> reporter -> END

The LOOP is the whole point of this pattern. `route` is a conditional edge that sends control BACK
to the generator to refine again, or forward to the reporter to finish. The decision is made by
`should_stop` in stopping.py — plain deterministic Python, never an LLM call. This back-edge is
exactly what LangGraph gives us over a straight-line LangChain chain.
"""
from langgraph.graph import END, START, StateGraph

from nodes.check import check
from nodes.evaluator import evaluate
from nodes.generator import generate
from nodes.reporter import report
from state import DesignState
from stopping import should_stop


def route(state: DesignState) -> str:
    """Conditional edge after the stopping-condition node: loop back or finish."""
    stop, _reason = should_stop(state)
    return "reporter" if stop else "generator"


def build_graph():
    """Build and compile the evaluator-optimizer graph."""
    graph = StateGraph(DesignState)
    graph.add_node("generator", generate)
    graph.add_node("evaluator", evaluate)
    graph.add_node("check", check)
    graph.add_node("reporter", report)

    graph.add_edge(START, "generator")
    graph.add_edge("generator", "evaluator")
    graph.add_edge("evaluator", "check")
    # The loop: from the stopping-condition node, branch back to "generator" or on to "reporter".
    graph.add_conditional_edges("check", route, ["generator", "reporter"])
    graph.add_edge("reporter", END)

    return graph.compile()

# Orchestrator-Workers: Research Report Generator

## What is Orchestrator-Workers?

In the **Orchestrator-Workers** pattern, a central **orchestrator** LLM breaks a task into subtasks
*at runtime*, dispatches a **worker** for each subtask, and a **synthesizer** combines the workers'
outputs into a final result. Unlike the Sectioning pattern (where the subtasks are fixed in advance),
here the orchestrator **decides how many subtasks there are and what they are** based on the input.

This example generates a research report: the orchestrator reads a topic, decides the research
angles, a worker researches each angle on the web, and a synthesizer writes the final report.

## Why LangGraph instead of plain LangChain?

A plain LangChain chain is a **static** pipeline — you wire the steps when you write the code. But
here the number of workers is **not known until the orchestrator runs**. LangGraph adds exactly what
this needs:

1. **The `Send` API** — a conditional edge returns a list of `Send("worker", payload)` objects, one
   per angle, fanning out a *runtime-decided* number of worker invocations.
2. **State reducers** — `sections: Annotated[list[Section], operator.add]` lets the concurrently
   running workers each append their section into one shared list without overwriting each other.
3. **Explicit state + graph** — nodes communicate through a typed `ResearchState` object, making the
   orchestrator → workers → synthesizer flow clear and inspectable.

## The flow

```
        --topic "Impact of AI on Healthcare" [--depth Deep]
                          │
                          ▼
   ┌────────────────────────────────────┐
   │ STEP 1 — orchestrator (orchestrator.py)
   │   LLM decides depth (if unset) + angles
   └────────────────────────────────────┘
                          │  angles
                          ▼   (route_to_workers: one Send per angle)
   ┌────────────────────────────────────┐
   │ STEP 2 — worker (worker.py) × N      │  run CONCURRENTLY
   │   Tavily search → LLM section draft  │  results merged by operator.add reducer
   └────────────────────────────────────┘
                          │  sections
                          ▼
   ┌────────────────────────────────────┐
   │ STEP 3 — synthesizer (synthesizer.py)│  one LLM call → cohesive report + insights
   └────────────────────────────────────┘
                          │
                          ▼  printed summary + saved to outputs/<slug>-<timestamp>.md
```

## How the dynamic task breakdown works

- The **orchestrator** makes one structured-output LLM call returning an `AnglePlan` (a chosen
  `depth` plus a list of `Angle`s, each with a `title` and a guiding `focus` question).
- `route_to_workers` in `graph.py` turns that list into `Send` objects:
  `[Send("worker", {topic, angle, index}) for i, angle in enumerate(angles, 1)]`. The graph runs
  one worker invocation per `Send`. Add a topic that needs 4 angles and you get 4 workers; one that
  needs 7 gives 7 — nothing is hardcoded.
- Each **worker** runs Tavily for its angle's focus question, drafts a markdown section, and returns
  `{"sections": [section]}`. Because workers run concurrently, the `[Angle N: ...] Complete` lines
  may print out of order — that is the visible proof of parallel fan-out.
- The **synthesizer** sorts the sections back into angle order and writes the final cohesive report.

## How to run

1. Make sure dependencies are installed and your env is set up (see the [root README](../../README.md)).
2. Add a Tavily key to `.env`: `TAVILY_API_KEY=tvly-...` (free key at https://tavily.com).
3. Run:

```bash
# Let the orchestrator decide the depth:
uv run python src/4-orchestrator-workers/main.py --topic "Impact of AI on Healthcare"

# Or force Quick / Deep:
uv run python src/4-orchestrator-workers/main.py --topic "Impact of AI on Healthcare" --depth Deep
```

The report summary is printed to the terminal and the full report is saved as markdown in
`src/4-orchestrator-workers/outputs/`.

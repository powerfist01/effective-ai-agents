# Evaluator-Optimizer: System Design Proposal Generator

## What is Evaluator-Optimizer?

In the **Evaluator-Optimizer** pattern, two LLM roles work in a feedback loop:

- A **generator** produces a first attempt at a task.
- An **evaluator** scores and critiques that attempt against explicit criteria.
- The generator **refines** its work using the critique, and the cycle repeats.

It mirrors how a human iterates with a reviewer: draft → feedback → revise → feedback → … until the
work is good enough. It shines when you have **clear quality criteria** and refinement actually
helps — code that must pass tests, writing that must hit a rubric, or, here, a system design scored
on concrete engineering dimensions.

This example designs software systems. You give it a problem (`"Design a URL shortener like Bitly"`)
and optional constraints; a generator drafts a structured design (requirements, architecture,
database, scalability, reliability, trade-offs); an evaluator scores it 1-10 on **Scalability,
Reliability, Simplicity, Cost Efficiency, Completeness** with one critique each; and the generator
refines until the design clears the quality bar.

## Why loops need stopping conditions

A naive "keep refining until it's perfect" loop never ends — an evaluator can always find *something*
to critique, and an LLM judge is noisy enough that scores can even wobble downward. So the loop needs
**deterministic stopping conditions**, evaluated by code (not by a model) after every round:

1. **Quality threshold met** — every dimension scores `>= 8/10` → stop, we converged.
2. **Max iterations reached** — `5` iterations done without converging → stop anyway, and return the
   **highest-scoring** iteration we produced (refinement isn't monotonic, so the last attempt isn't
   always the best).

Keeping this logic in plain Python (`stopping.py`) makes it predictable and unit-testable. The LLM
*scores*; the code *decides*.

## Why LangGraph instead of plain LangChain?

A plain LangChain chain is a straight line — it can't point an edge back at an earlier step. This
pattern is fundamentally a **cycle**, and LangGraph gives us exactly that:

1. **A conditional back-edge** — after the stopping-condition node, `route` returns `"generator"`
   (loop back and refine) or `"reporter"` (finish). That back-edge is the loop.
2. **Explicit, typed state** — `DesignState` carries the problem, the iteration counter, the full
   history of designs + evaluations, the best-iteration tracker, and the final report. Every node
   reads and writes this one object.
3. **Deterministic control flow** — the looping/stopping decision is ordinary code on the state,
   cleanly separated from the LLM calls inside the nodes.

## The flow

```
   --problem "Design a URL shortener like Bitly" [--constraints "..."]
                          │
                          ▼
   ┌───────────────────────────────────────────┐   ◀─────────────────────┐
   │ generator (generator.py)                    │                         │
   │   iter 1: draft initial design              │                         │
   │   iter N: refine using FULL feedback history│                         │ "generator"
   └───────────────────────────────────────────┘                         │ (loop back
                          │  current_design                                │  & refine)
                          ▼                                                 │
   ┌───────────────────────────────────────────┐                         │
   │ evaluator (evaluator.py)                    │                         │
   │   score 1-10 × 5 dimensions + 1 critique ea │                         │
   └───────────────────────────────────────────┘                         │
                          │  append to history                             │
                          ▼                                                 │
   ┌───────────────────────────────────────────┐                         │
   │ check (check.py) — DETERMINISTIC, no LLM    │── route(state) ─────────┘
   │   converged? max iters? update best tracker │
   └───────────────────────────────────────────┘
                          │ "reporter" (stop)
                          ▼
   ┌───────────────────────────────────────────┐
   │ reporter (reporter.py)                      │  iteration-history summary
   │   build full markdown report                │  + saved to outputs/<slug>-<timestamp>.md
   └───────────────────────────────────────────┘
```

## How the scoring and refinement works

- **Scoring.** The evaluator makes one `with_structured_output(Evaluation)` call. `Evaluation` is a
  flat Pydantic model with a `1-10` score and a critique per dimension; `scores()`, `critiques()`,
  and `average()` re-key them by dimension name for display and the stopping check.
- **Stopping (`stopping.py`).** `is_converged` is `all(score >= threshold)`. `should_stop` returns
  `(stop, reason)` where reason is `converged` / `max_iterations` / `continue`. Both the `check` node
  and the `route` edge call these same helpers, so the printed status and the branch taken always
  agree.
- **Refinement.** On every loop after the first, the generator receives the **original problem**, the
  **full history** of past designs and their feedback, **and** the latest critique as an explicit
  to-do list — then must address each critique. Feeding the whole history (not just the last note)
  stops it from re-introducing problems earlier rounds already fixed.
- **Best-iteration tracker.** `check` records the highest-scoring iteration each round. If we hit the
  iteration cap without converging, the reporter returns that best design rather than the last one.

### Sample terminal output

```
===== ITERATION 1: Generating System Design =====
Problem: Design a URL shortener like Bitly
Generating initial proposal...

===== ITERATION 1: Evaluating Design =====
Scalability:     6/10 - No caching strategy mentioned
Reliability:     7/10 - Missing failover mechanism
Simplicity:      8/10 - Architecture is clean
Cost Efficiency: 6/10 - Database choice is expensive at scale
Completeness:    7/10 - API design not fully specified
Average Score:   6.8/10
Status: Below threshold — Refining...

... (iterations 2-3) ...

===== ITERATION HISTORY =====
Iteration 1 → Avg Score: 6.8/10
Iteration 2 → Avg Score: 7.4/10
Iteration 3 → Avg Score: 8.2/10  ✓ Threshold met!
```

## How to run

1. Make sure dependencies are installed and your env is set up (see the [root README](../../README.md)).
   This pattern needs no extra keys beyond your LLM choice (Anthropic or Ollama) — no web search.
2. Run:

```bash
# Simplest — just a problem statement:
uv run python src/5-evaluator-optimizer/main.py --problem "Design a URL shortener like Bitly"

# With constraints, and a stricter / longer loop:
uv run python src/5-evaluator-optimizer/main.py \
    --problem "Design a real-time chat system like WhatsApp" \
    --constraints "100M users, must use PostgreSQL, tight budget" \
    --max-iterations 5 --threshold 8
```

Flags: `--constraints` (optional context), `--max-iterations` (default `5`), `--threshold`
(default `8`, the per-dimension bar to converge).

The iteration history is printed to the terminal and the full report — problem, constraints,
iteration history with per-dimension scores and feedback, a convergence note, and the final design
in full — is saved to `src/5-evaluator-optimizer/outputs/`.

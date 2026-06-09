# Pattern 3: Parallelization

## What is Parallelization?

Parallelization is a pattern where multiple LLM calls run **at the same time** instead of one after
another. Because each call is an independent, network-bound request, running them concurrently can
turn four sequential 5-second calls into a single 5-second wall-clock wait — and it often *improves*
quality too, since each call gets a narrow, focused job instead of one overloaded prompt.

There are two common sub-patterns:

| Sub-pattern | Idea | Status |
|-------------|------|--------|
| [**Sectioning**](1-sectioning/README.md) | Split one job into **different** independent sub-tasks, run them in parallel, then **merge** the results. | ✅ Built |
| [**Voting**](2-voting/README.md) | Run the **same** task multiple times (different prompts/models/seeds) and aggregate by **consensus** for higher confidence. | 🚧 Coming Soon |

### Sectioning vs Voting

- **Sectioning** = *divide and conquer*. The sub-tasks are **distinct** (e.g. "find the pros" vs
  "find the cons"). Each answers a different question about the same input, and the answers are
  combined into a richer whole.
- **Voting** = *ask the same question several times*. The sub-tasks are **identical** (or near
  identical). You aggregate them — by majority, averaging, or a final judge — to reduce the chance
  of a single bad answer. Useful for subjective or error-prone judgments.

This folder demonstrates **Sectioning**. Voting will be added later.

## Sub-folders

- [`1-sectioning/`](1-sectioning/README.md) — Product Review Analyzer: fetch reviews, then run four
  independent analyses simultaneously and aggregate them.
- [`2-voting/`](2-voting/README.md) — Coming Soon.

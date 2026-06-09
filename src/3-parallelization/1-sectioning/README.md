# Sectioning: Product Review Analyzer

## What is Sectioning?

**Sectioning** is the "divide and conquer" form of parallelization. You take one big job, break it
into **independent sub-tasks that each answer a different question**, run them all at the same time,
and then **merge** their outputs into a single result. Because the sub-tasks don't depend on each
other, there is no reason to run them sequentially.

## Why this example?

Analyzing product reviews is a natural fit. Given the same pile of reviews, you can ask four
genuinely independent questions:

1. **Sentiment** — is the overall verdict positive, negative, or mixed?
2. **Pros** — what do people consistently love?
3. **Cons** — what do people consistently dislike?
4. **Target audience** — who is this product best for?

None of these answers needs any of the others, so they are perfect sections to run in parallel.

## The flow

```
        --product "Sony WH-1000XM5"
                  │
                  ▼
   ┌──────────────────────────────┐
   │ STEP 1 — Fetch (fetcher.py)   │  Tavily web search → one "review corpus"
   └──────────────────────────────┘
                  │  corpus
                  ▼
   ┌──────────────────────────────┐
   │ STEP 2 — Parallel (asyncio)   │   all four run at the SAME time
   │   ├─ sentiment.py             │
   │   ├─ pros.py                  │
   │   ├─ cons.py                  │
   │   └─ audience.py              │
   └──────────────────────────────┘
                  │  4 results
                  ▼
   ┌──────────────────────────────┐
   │ STEP 3 — Aggregate            │   deterministic templating, no LLM call
   │   (aggregator.py)             │   → printed + saved to outputs/
   └──────────────────────────────┘
```

## How the parallel tasks work

- Each analyzer is a **self-contained unit**: a `ChatPromptTemplate` plus an `async def run(corpus, llm)`
  that builds a small LangChain chain (`prompt | llm | parser`) and `ainvoke`s it. They are distinct,
  readable files — not one giant prompt.
- `main.py` runs them together with **`asyncio.gather`**. Each task prints a `[Name] Complete` line
  the moment *it* finishes. Because they run concurrently, those lines **interleave out of order** —
  that's your visual proof the work is simultaneous, not sequential.
- **Sentiment** uses LangChain **structured output** (a Pydantic `SentimentResult` with a
  `verdict` of `Positive`/`Negative`/`Mixed`), so we can print a clean `[Sentiment] Complete: Positive`.
  The other three return markdown text.
- **Aggregation** (`aggregator.py`) is pure Python string templating — the four sections are already
  complete, so merging them needs no extra LLM call. The report is printed and saved to `outputs/`.

## How to run

1. Make sure dependencies are installed and your env is set up (see the [root README](../../../README.md)).
2. Add a Tavily key to `.env`: `TAVILY_API_KEY=tvly-...` (free key at https://tavily.com).
3. Run:

```bash
uv run python src/3-parallelization/1-sectioning/main.py --product "Sony WH-1000XM5"
```

The final report is printed to the terminal and saved as a markdown file in
`src/3-parallelization/1-sectioning/outputs/`.

# Effective Agents

A hands-on learning repo for understanding LangChain and LangGraph patterns through real examples.

Each pattern lives in its own directory under `src/`. They share a common LLM config in `config/`.

## Patterns

| # | Pattern | Description |
|---|---------|-------------|
| 1 | [Prompt Chaining](src/1-prompt-chaining/README.md) | Sequential LLM steps where each output feeds the next |
| 2 | [Routing](src/2-routing/README.md) | Classify input with an LLM, then dispatch to a specialized handler |
| 3 | [Parallelization](src/3-parallelization/README.md) | Run independent analysis tasks simultaneously, then aggregate the results |
| 4 | [Orchestrator-Workers](src/4-orchestrator-workers/README.md) | An orchestrator LLM dynamically splits a task into subtasks, workers run each in parallel, and a synthesizer combines them |
| 5 | [Evaluator-Optimizer](src/5-evaluator-optimizer/README.md) | A generator LLM drafts, an evaluator LLM scores and critiques, and the generator refines in a loop until a quality threshold is met or iterations run out |

## Setup

**Prerequisites:** Python 3.11+, [uv](https://docs.astral.sh/uv/)

```bash
# Install dependencies
uv sync

# Copy and fill in your env file
cp .env.example .env
```

**LLM options:**

- **Anthropic (Claude):** Add `ANTHROPIC_API_KEY=sk-ant-...` to `.env`
- **Ollama (local):** Leave `ANTHROPIC_API_KEY` unset and run `ollama serve` with `ollama pull llama3.2`

## Resume Setup

Place your resume PDF at `data/resume.pdf`. This file is git-ignored — it stays local.

## Running Tests

```bash
uv run pytest tests/ -v
```

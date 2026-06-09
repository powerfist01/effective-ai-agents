# Pattern 2: Routing

## What is Routing?

Routing is a pattern where an LLM first classifies an input, then the result determines which
processing path runs next. Instead of one giant prompt trying to handle all cases, you split the
work: a lightweight classifier decides *what kind* of thing this is, then a specialized handler
takes over.

**Why does this matter?**
- Each specialized handler can be tuned for its specific case — no compromises
- The classifier stays focused on a single decision, making it easier to reason about and test
- Adding a new route means adding one new handler file — the classifier and orchestrator barely change

## This Example: Content Router

The router takes a topic and optional context, and produces platform-ready content in two stages:

```
Topic + Context
      │
      ▼
  Classifier (Stage 1)
  → Detects the best platform: Blog / Email / LinkedIn / Reddit / Facebook / X
  → Explains its reasoning
      │
      ▼
  Specialized Writer (Stage 2)
  → Routed to the right writer based on the classification
  → Streams the finished, platform-ready content
```

### How classification works

The classifier uses **Pydantic structured output** via LangChain's `with_structured_output()`. This
constrains the LLM to return a typed object — a `format` field that must be one of the six exact
platform names, and a `reason` field. There is no string parsing or post-processing: the model
either returns a valid object or raises an error.

### How routing works

`main.py` holds a `WRITERS` dict that maps each platform name to its writer module's `run()`
function. After classification, a single dict lookup dispatches to the right writer. No if/else
chains, no switch statements.

```python
WRITERS = {
    "Blog": blog.run,
    "Email": email.run,
    "LinkedIn": linkedin.run,
    "Reddit": reddit.run,
    "Facebook": facebook.run,
    "X": x_writer.run,
}
writer_fn = WRITERS[classification.format]
```

## How to Run

```bash
uv run python src/2-routing/main.py \
  --topic "I just got promoted to Staff Engineer" \
  --context "Sharing the news with my professional network"
```

Context is optional:

```bash
uv run python src/2-routing/main.py --topic "Why sleep matters for developers"
```

## Code Structure

```
src/2-routing/
├── main.py               # CLI entry point, orchestration, WRITERS dispatch dict
├── classifier.py         # ClassificationResult Pydantic model + structured output chain
├── writers/              # One file per platform — each is a self-contained LCEL chain
│   ├── __init__.py
│   ├── blog.py
│   ├── email.py
│   ├── linkedin.py
│   ├── reddit.py
│   ├── facebook.py
│   └── x.py
└── README.md
```

Each writer file follows the same three-part pattern (identical to Pattern 1):
1. `_prompt` — the `ChatPromptTemplate` with platform-specific instructions
2. `_build_chain(llm)` — assembles the LCEL chain: `prompt | llm | StrOutputParser()`
3. `run(topic, context, llm)` — public function that returns a streaming generator

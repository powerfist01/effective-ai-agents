# Pattern 1: Prompt Chaining

## What is Prompt Chaining?

Prompt chaining is a pattern where the output of one LLM call becomes the input to the next. Each step has a focused task; together they accomplish something more complex than any single prompt could reliably handle.

**Why break it into steps?**
- Each prompt stays focused and short — better quality output
- You can inspect and debug each stage independently
- Failed steps can be retried without rerunning the whole chain

## This Example: Job Application Helper

The chain takes a raw job description and a resume PDF and produces five outputs:

```
Raw JD Text ──► Step 1: Structure JD ──► Structured Markdown JD
                                                │
PDF Resume ──► Step 2: Clean Resume ──► Cleaned Resume Text
                                                │
                        ┌───────────────────────┘
                        ▼
              Step 3: Gap Analysis ──► Matches & Gaps
                        │
                        ▼
              Step 4: Cover Letter ──► Personalized Letter
                        │
                        ▼
              Step 5: Interview Prep ──► 10 Likely Questions
```

## Prerequisites

Place your resume PDF at `data/resume.pdf` in the project root (git-ignored).

## How to Run

```bash
uv run python src/1-prompt-chaining/main.py \
  --jd src/1-prompt-chaining/samples/sample_jd.txt \
  --resume data/resume.pdf
```

To use a different job description, pass any plain-text `.txt` file to `--jd`.

## Code Structure

```
src/1-prompt-chaining/
├── main.py               # CLI entry point + orchestrator
├── steps/                # One file per step — each is a self-contained LCEL chain
│   ├── step1_structure_jd.py
│   ├── step2_extract_resume.py
│   ├── step3_gap_analysis.py
│   ├── step4_cover_letter.py
│   └── step5_interview_prep.py
├── utils/
│   └── pdf_reader.py     # PDF text extraction (no LLM)
└── samples/
    └── sample_jd.txt     # Sample job description for quick testing
```

Each step file follows the same pattern:
1. `_prompt` — the `ChatPromptTemplate` with the task instructions
2. `_build_chain(llm)` — assembles the LCEL chain: `prompt | llm | StrOutputParser()`
3. `run(...)` — public function that returns a streaming generator of text chunks

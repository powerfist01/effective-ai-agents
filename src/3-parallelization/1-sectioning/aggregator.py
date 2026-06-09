"""Stage 3 — deterministically assemble the four analyzer outputs into one markdown report.

No LLM call: each section is already complete, so this is pure templating. This is the "merge"
half of the Sectioning pattern.
"""
import re
from pathlib import Path

_OUTPUTS_DIR = Path(__file__).parent / "outputs"


def slugify(text: str) -> str:
    """Lowercase, strip punctuation, collapse whitespace to single hyphens."""
    text = text.lower().strip()
    text = re.sub(r"[^a-z0-9\s-]", "", text)   # drop punctuation
    text = re.sub(r"[\s_]+", "-", text)         # spaces/underscores -> hyphen
    text = re.sub(r"-+", "-", text)             # collapse repeats
    return text.strip("-")


def build_report(product, sentiment, sentiment_reason, pros, cons, audience) -> str:
    """Assemble the unified markdown report from the four parallel outputs."""
    return f"""# Product Review Analysis: {product}

**Sentiment:** {sentiment}

> {sentiment_reason}

## What People Love
{pros}

## Common Complaints
{cons}

## Best For
{audience}
"""


def save_report(product: str, report: str, timestamp: str) -> Path:
    """Write the report to outputs/{slug}-{timestamp}.md and return the path."""
    _OUTPUTS_DIR.mkdir(exist_ok=True)
    path = _OUTPUTS_DIR / f"{slugify(product)}-{timestamp}.md"
    path.write_text(report, encoding="utf-8")
    return path

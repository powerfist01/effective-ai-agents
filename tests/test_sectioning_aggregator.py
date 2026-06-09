import sys
from pathlib import Path

_SECTIONING = Path(__file__).parent.parent / "src" / "3-parallelization" / "1-sectioning"
sys.path.insert(0, str(_SECTIONING))

import aggregator  # noqa: E402


def test_slugify_basic():
    assert aggregator.slugify("Sony WH-1000XM5") == "sony-wh-1000xm5"


def test_slugify_strips_punctuation_and_collapses_spaces():
    assert aggregator.slugify("  Apple   iPhone 15 Pro!! ") == "apple-iphone-15-pro"


def test_build_report_contains_all_sections():
    report = aggregator.build_report(
        product="Sony WH-1000XM5",
        sentiment="Positive",
        sentiment_reason="Most reviews praise the noise cancellation.",
        pros="- Great ANC\n- Comfortable",
        cons="- Expensive",
        audience="Frequent travelers.",
    )
    assert "# Product Review Analysis: Sony WH-1000XM5" in report
    assert "**Sentiment:** Positive" in report
    assert "Most reviews praise the noise cancellation." in report
    assert "- Great ANC" in report
    assert "- Expensive" in report
    assert "Frequent travelers." in report
    assert "## Best For" in report

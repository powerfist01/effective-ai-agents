import importlib.util
import sys
from pathlib import Path

import pytest

_PATTERN = Path(__file__).parent.parent / "src" / "4-orchestrator-workers"


@pytest.fixture(autouse=True)
def _isolate_pattern_modules():
    """Make this pattern's bare module names resolve to THIS pattern, per test.

    Patterns 4 and 5 both ship modules named `state`, `graph`, `nodes`, etc. and import them by
    bare name, so a full `pytest tests/` run would otherwise serve whichever pattern imported first.
    Putting this pattern's dir first and evicting the shared names per-test keeps them isolated.
    """
    if str(_PATTERN) in sys.path:
        sys.path.remove(str(_PATTERN))
    sys.path.insert(0, str(_PATTERN))
    for name in list(sys.modules):
        if name in {"state", "graph", "stopping"} or name == "nodes" or name.startswith("nodes."):
            del sys.modules[name]
    yield


def _load_main():
    """Load this pattern's main.py under a unique module name.

    A plain `import main` collides with pattern 1's main.py, which pytest may have already
    cached in sys.modules during the same run. Loading by file path under a unique name keeps
    the two patterns' `main` modules isolated.
    """
    spec = importlib.util.spec_from_file_location("ow_main", _PATTERN / "main.py")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def test_section_defaults_sources_to_empty_list():
    from state import Section
    s = Section(index=1, title="Ethics", body="text")
    assert s.sources == []


def test_angle_requires_title_and_focus():
    from state import Angle
    a = Angle(title="Ethics", focus="What ethical concerns arise?")
    assert a.title == "Ethics"
    assert a.focus.startswith("What")


def test_depth_instructions_quick_mentions_3_4():
    from nodes import orchestrator
    text = orchestrator._depth_instructions("Quick")
    assert "3-4" in text


def test_depth_instructions_deep_mentions_6_8():
    from nodes import orchestrator
    text = orchestrator._depth_instructions("Deep")
    assert "6-8" in text


def test_depth_instructions_none_lets_llm_decide():
    from nodes import orchestrator
    text = orchestrator._depth_instructions(None)
    assert "decide" in text.lower()


def test_orchestrator_prompt_includes_topic_and_instructions():
    from nodes import orchestrator
    messages = orchestrator._prompt.format_messages(
        topic="AI in Healthcare", depth_instructions="PICK 5 ANGLES"
    )
    content = messages[0].content
    assert "AI in Healthcare" in content
    assert "PICK 5 ANGLES" in content


def test_build_query_combines_topic_and_focus():
    from nodes import worker
    from state import Angle
    angle = Angle(title="Ethics", focus="What ethical concerns arise?")
    query = worker._build_query("AI in Healthcare", angle)
    assert "AI in Healthcare" in query
    assert "What ethical concerns arise?" in query


def test_worker_prompt_includes_corpus_and_angle():
    from nodes import worker
    messages = worker._prompt.format_messages(
        topic="AI in Healthcare",
        title="Ethics",
        focus="What ethical concerns arise?",
        corpus="[Source 1] Some article text",
    )
    content = messages[0].content
    assert "Some article text" in content
    assert "Ethics" in content


def test_format_sections_orders_by_index():
    from nodes import synthesizer
    from state import Section
    sections = [
        Section(index=2, title="Second", body="B"),
        Section(index=1, title="First", body="A"),
    ]
    out = synthesizer._format_sections(sections)
    assert out.index("First") < out.index("Second")


def test_synthesizer_prompt_includes_topic_and_sections():
    from nodes import synthesizer
    messages = synthesizer._prompt.format_messages(
        topic="AI in Healthcare", sections="### First\nA"
    )
    content = messages[0].content
    assert "AI in Healthcare" in content
    assert "### First" in content


def test_route_to_workers_one_send_per_angle():
    import graph
    from state import Angle
    state = {
        "topic": "AI in Healthcare",
        "angles": [
            Angle(title="A", focus="fa"),
            Angle(title="B", focus="fb"),
        ],
    }
    sends = graph.route_to_workers(state)
    assert len(sends) == 2
    assert all(s.node == "worker" for s in sends)
    # Each Send carries its topic, angle, and 1-based index.
    assert sends[0].arg["index"] == 1
    assert sends[1].arg["index"] == 2
    assert sends[0].arg["angle"].title == "A"
    assert sends[0].arg["topic"] == "AI in Healthcare"


def test_build_graph_compiles():
    import graph
    app = graph.build_graph()
    assert app is not None


def test_slugify_basic():
    main = _load_main()
    assert main.slugify("Impact of AI on Healthcare!") == "impact-of-ai-on-healthcare"


def test_save_report_writes_markdown(tmp_path):
    main = _load_main()
    path = main.save_report("AI in Healthcare", "# Report\nbody", "20260601-120000",
                            out_dir=tmp_path)
    assert path.exists()
    assert path.name == "ai-in-healthcare-20260601-120000.md"
    assert path.read_text(encoding="utf-8") == "# Report\nbody"

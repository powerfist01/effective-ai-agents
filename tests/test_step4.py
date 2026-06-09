from unittest.mock import MagicMock
import steps.step4_cover_letter as step4


def test_prompt_template_includes_both_inputs():
    messages = step4._prompt.format_messages(
        structured_jd="Senior Python Developer",
        gap_analysis="Gaps: no Go experience",
    )
    content = messages[0].content
    assert "Senior Python Developer" in content
    assert "Gaps: no Go experience" in content


def test_run_passes_both_inputs_to_chain(monkeypatch):
    mock_chain = MagicMock()
    mock_chain.stream.return_value = iter(["Dear Hiring Manager,\n"])
    monkeypatch.setattr(step4, "get_llm", lambda: MagicMock())
    monkeypatch.setattr(step4, "_build_chain", lambda llm: mock_chain)

    chunks = list(step4.run("structured jd", "gap analysis"))

    mock_chain.stream.assert_called_once_with({
        "structured_jd": "structured jd",
        "gap_analysis": "gap analysis",
    })
    assert chunks == ["Dear Hiring Manager,\n"]


def test_run_uses_provided_llm(monkeypatch):
    mock_llm = MagicMock()
    captured = {}

    def fake_build_chain(llm):
        captured["llm"] = llm
        mock_chain = MagicMock()
        mock_chain.stream.return_value = iter([])
        return mock_chain

    monkeypatch.setattr(step4, "_build_chain", fake_build_chain)
    list(step4.run("jd", "gaps", llm=mock_llm))
    assert captured["llm"] is mock_llm

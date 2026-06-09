from unittest.mock import MagicMock
import steps.step5_interview_prep as step5


def test_prompt_template_includes_all_three_inputs():
    messages = step5._prompt.format_messages(
        structured_jd="Senior Python Developer",
        resume_text="5 years Python",
        gap_analysis="Gaps: no Kubernetes",
    )
    content = messages[0].content
    assert "Senior Python Developer" in content
    assert "5 years Python" in content
    assert "Gaps: no Kubernetes" in content


def test_run_passes_all_inputs_to_chain(monkeypatch):
    mock_chain = MagicMock()
    mock_chain.stream.return_value = iter(["1. Tell me about yourself\n"])
    monkeypatch.setattr(step5, "get_llm", lambda: MagicMock())
    monkeypatch.setattr(step5, "_build_chain", lambda llm: mock_chain)

    chunks = list(step5.run("structured jd", "resume text", "gap analysis"))

    mock_chain.stream.assert_called_once_with({
        "structured_jd": "structured jd",
        "resume_text": "resume text",
        "gap_analysis": "gap analysis",
    })
    assert chunks == ["1. Tell me about yourself\n"]


def test_run_uses_provided_llm(monkeypatch):
    mock_llm = MagicMock()
    captured = {}

    def fake_build_chain(llm):
        captured["llm"] = llm
        mock_chain = MagicMock()
        mock_chain.stream.return_value = iter([])
        return mock_chain

    monkeypatch.setattr(step5, "_build_chain", fake_build_chain)
    list(step5.run("jd", "resume", "gaps", llm=mock_llm))
    assert captured["llm"] is mock_llm

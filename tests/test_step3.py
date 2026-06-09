from unittest.mock import MagicMock
import steps.step3_gap_analysis as step3


def test_prompt_template_includes_both_inputs():
    messages = step3._prompt.format_messages(
        structured_jd="Senior Python Developer role",
        resume_text="5 years Python experience",
    )
    content = messages[0].content
    assert "Senior Python Developer role" in content
    assert "5 years Python experience" in content


def test_run_passes_both_inputs_to_chain(monkeypatch):
    mock_chain = MagicMock()
    mock_chain.stream.return_value = iter(["## Strong Matches\n", "Python\n"])
    monkeypatch.setattr(step3, "get_llm", lambda: MagicMock())
    monkeypatch.setattr(step3, "_build_chain", lambda llm: mock_chain)

    chunks = list(step3.run("structured jd", "resume text"))

    mock_chain.stream.assert_called_once_with({
        "structured_jd": "structured jd",
        "resume_text": "resume text",
    })
    assert chunks == ["## Strong Matches\n", "Python\n"]


def test_run_uses_provided_llm(monkeypatch):
    mock_llm = MagicMock()
    captured = {}

    def fake_build_chain(llm):
        captured["llm"] = llm
        mock_chain = MagicMock()
        mock_chain.stream.return_value = iter([])
        return mock_chain

    monkeypatch.setattr(step3, "_build_chain", fake_build_chain)
    list(step3.run("jd", "resume", llm=mock_llm))
    assert captured["llm"] is mock_llm

from unittest.mock import MagicMock
import steps.step2_extract_resume as step2


def test_prompt_template_includes_resume_raw():
    messages = step2._prompt.format_messages(resume_raw="John Doe  S o f t w a r e  Engineer")
    assert "John Doe" in messages[0].content


def test_run_passes_resume_raw_to_chain(monkeypatch):
    mock_chain = MagicMock()
    mock_chain.stream.return_value = iter(["John Doe\n", "Software Engineer\n"])
    monkeypatch.setattr(step2, "get_llm", lambda: MagicMock())
    monkeypatch.setattr(step2, "_build_chain", lambda llm: mock_chain)

    chunks = list(step2.run("raw resume text"))

    mock_chain.stream.assert_called_once_with({"resume_raw": "raw resume text"})
    assert chunks == ["John Doe\n", "Software Engineer\n"]


def test_run_uses_provided_llm(monkeypatch):
    mock_llm = MagicMock()
    captured = {}

    def fake_build_chain(llm):
        captured["llm"] = llm
        mock_chain = MagicMock()
        mock_chain.stream.return_value = iter([])
        return mock_chain

    monkeypatch.setattr(step2, "_build_chain", fake_build_chain)
    list(step2.run("resume text", llm=mock_llm))
    assert captured["llm"] is mock_llm

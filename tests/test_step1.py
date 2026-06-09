from unittest.mock import MagicMock
import steps.step1_structure_jd as step1


def test_prompt_template_includes_jd_raw():
    messages = step1._prompt.format_messages(jd_raw="Software Engineer at Acme Corp")
    assert "Software Engineer at Acme Corp" in messages[0].content


def test_run_passes_jd_raw_to_chain(monkeypatch):
    mock_chain = MagicMock()
    mock_chain.stream.return_value = iter(["# Job Title\n", "Engineer\n"])
    monkeypatch.setattr(step1, "get_llm", lambda: MagicMock())
    monkeypatch.setattr(step1, "_build_chain", lambda llm: mock_chain)

    chunks = list(step1.run("raw jd text"))

    mock_chain.stream.assert_called_once_with({"jd_raw": "raw jd text"})
    assert chunks == ["# Job Title\n", "Engineer\n"]


def test_run_uses_provided_llm(monkeypatch):
    mock_llm = MagicMock()
    captured = {}

    def fake_build_chain(llm):
        captured["llm"] = llm
        mock_chain = MagicMock()
        mock_chain.stream.return_value = iter([])
        return mock_chain

    monkeypatch.setattr(step1, "_build_chain", fake_build_chain)
    list(step1.run("jd text", llm=mock_llm))
    assert captured["llm"] is mock_llm

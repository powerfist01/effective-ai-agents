import sys
import pytest
from pathlib import Path

import main as main_module
from main import parse_args, stream_step, main


def test_parse_args_requires_jd(monkeypatch):
    monkeypatch.setattr(sys, "argv", ["main.py", "--resume", "resume.pdf"])
    with pytest.raises(SystemExit):
        parse_args()


def test_parse_args_requires_resume(monkeypatch):
    monkeypatch.setattr(sys, "argv", ["main.py", "--jd", "jd.txt"])
    with pytest.raises(SystemExit):
        parse_args()


def test_parse_args_returns_both_paths(monkeypatch):
    monkeypatch.setattr(sys, "argv", ["main.py", "--jd", "jd.txt", "--resume", "resume.pdf"])
    args = parse_args()
    assert args.jd == "jd.txt"
    assert args.resume == "resume.pdf"


def test_stream_step_returns_concatenated_chunks(capsys):
    result = stream_step("STEP 1: Test", iter(["Hello ", "World"]))
    assert result == "Hello World"


def test_stream_step_prints_banner(capsys):
    stream_step("STEP 1: Test", iter(["data"]))
    captured = capsys.readouterr()
    assert "STEP 1: Test" in captured.out


def test_main_exits_when_jd_file_not_found(monkeypatch, tmp_path, capsys):
    resume = tmp_path / "resume.pdf"
    resume.write_bytes(b"fake")
    monkeypatch.setattr(sys, "argv", [
        "main.py", "--jd", "/nonexistent/jd.txt", "--resume", str(resume)
    ])
    monkeypatch.setattr(main_module, "load_dotenv", lambda: None)

    with pytest.raises(SystemExit) as exc_info:
        main()

    assert exc_info.value.code == 1
    captured = capsys.readouterr()
    assert "not found" in captured.out


def test_main_exits_when_pdf_not_found(monkeypatch, tmp_path, capsys):
    jd = tmp_path / "jd.txt"
    jd.write_text("Software Engineer role")
    monkeypatch.setattr(sys, "argv", [
        "main.py", "--jd", str(jd), "--resume", "/nonexistent/resume.pdf"
    ])
    monkeypatch.setattr(main_module, "load_dotenv", lambda: None)

    with pytest.raises(SystemExit) as exc_info:
        main()

    assert exc_info.value.code == 1
    captured = capsys.readouterr()
    assert "not found" in captured.out

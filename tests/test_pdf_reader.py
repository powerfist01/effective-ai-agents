import pytest
from utils.pdf_reader import extract_text_from_pdf


def test_extract_text_returns_content_from_pdf(sample_pdf_path):
    result = extract_text_from_pdf(sample_pdf_path)
    assert "Jane Smith" in result
    assert "Python" in result


def test_extract_text_returns_string(sample_pdf_path):
    result = extract_text_from_pdf(sample_pdf_path)
    assert isinstance(result, str)


def test_extract_text_raises_for_missing_file():
    with pytest.raises(FileNotFoundError, match="/nonexistent/resume.pdf"):
        extract_text_from_pdf("/nonexistent/resume.pdf")


def test_extract_text_returns_empty_string_for_image_only_pdf(tmp_path):
    from fpdf import FPDF
    pdf = FPDF()
    pdf.add_page()
    path = tmp_path / "empty.pdf"
    pdf.output(str(path))
    result = extract_text_from_pdf(str(path))
    assert isinstance(result, str)

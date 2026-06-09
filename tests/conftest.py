import sys
from pathlib import Path
import pytest

# Project root (for config/)
_root = Path(__file__).parent.parent
# Pattern dir (for steps/, utils/)
_pattern = _root / "src" / "1-prompt-chaining"

for p in [str(_root), str(_pattern)]:
    if p not in sys.path:
        sys.path.insert(0, p)


@pytest.fixture
def sample_pdf_path(tmp_path):
    from fpdf import FPDF
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Helvetica", size=12)
    pdf.cell(200, 10, text="Jane Smith - Senior Python Developer", new_x="LMARGIN", new_y="NEXT")
    pdf.cell(200, 10, text="jane@example.com | github.com/janesmith", new_x="LMARGIN", new_y="NEXT")
    pdf.cell(200, 10, text="Experience: 6 years Python, 3 years FastAPI, 2 years AWS", new_x="LMARGIN", new_y="NEXT")
    pdf.cell(200, 10, text="Education: BSc Computer Science, State University 2018", new_x="LMARGIN", new_y="NEXT")
    path = tmp_path / "test_resume.pdf"
    pdf.output(str(path))
    return str(path)

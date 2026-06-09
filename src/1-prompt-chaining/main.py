import sys
from pathlib import Path

# Ensure imports resolve from both the project root (config/) and this directory (steps/, utils/)
_root = Path(__file__).parent.parent.parent
_here = Path(__file__).parent
for _p in [str(_root), str(_here)]:
    if _p not in sys.path:
        sys.path.insert(0, _p)

import argparse

from dotenv import load_dotenv

from steps import step1_structure_jd
from steps import step2_extract_resume
from steps import step3_gap_analysis
from steps import step4_cover_letter
from steps import step5_interview_prep
from utils.pdf_reader import extract_text_from_pdf


def parse_args():
    parser = argparse.ArgumentParser(description="Job Application Helper — Prompt Chaining")
    parser.add_argument("--jd", required=True, help="Path to job description text file")
    parser.add_argument("--resume", required=True, help="Path to resume PDF file")
    return parser.parse_args()


def stream_step(title: str, generator) -> str:
    print(f"\n{'=' * 5} {title} {'=' * 5}\n")
    result = ""
    for chunk in generator:
        print(chunk, end="", flush=True)
        result += chunk
    print("\n")
    return result


def main():
    load_dotenv()
    args = parse_args()

    jd_path = Path(args.jd)
    if not jd_path.exists():
        print(f"Error: JD file not found: {args.jd}")
        sys.exit(1)

    try:
        pdf_raw = extract_text_from_pdf(args.resume)
    except FileNotFoundError as e:
        print(f"Error: {e}")
        sys.exit(1)

    jd_raw = jd_path.read_text(encoding="utf-8")

    try:
        structured_jd = stream_step(
            "STEP 1: Structuring Job Description",
            step1_structure_jd.run(jd_raw),
        )
        resume_text = stream_step(
            "STEP 2: Cleaning Resume Text",
            step2_extract_resume.run(pdf_raw),
        )
        gap_analysis = stream_step(
            "STEP 3: Gap Analysis",
            step3_gap_analysis.run(structured_jd, resume_text),
        )
        stream_step(
            "STEP 4: Tailored Cover Letter",
            step4_cover_letter.run(structured_jd, gap_analysis),
        )
        stream_step(
            "STEP 5: Interview Prep Questions",
            step5_interview_prep.run(structured_jd, resume_text, gap_analysis),
        )
    except Exception as e:
        print(f"\nError running chain: {e}")
        print("If using Ollama: ensure it is running with `ollama serve`")
        print("If using Anthropic: check your ANTHROPIC_API_KEY in .env")
        sys.exit(1)


if __name__ == "__main__":
    main()

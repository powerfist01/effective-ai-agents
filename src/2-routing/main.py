import sys
from pathlib import Path

# Add project root (for config/) and this directory (for classifier, writers/) to sys.path.
# Same pattern as src/1-prompt-chaining/main.py.
_root = Path(__file__).parent.parent.parent
_here = Path(__file__).parent
for _p in [str(_root), str(_here)]:
    if _p not in sys.path:
        sys.path.insert(0, _p)

import argparse

from dotenv import load_dotenv

import classifier
from config.llm import get_llm
from writers import blog, email, linkedin, reddit, facebook
from writers import x as x_writer

# Maps each classifier output to its writer's run() function.
WRITERS = {
    "Blog": blog.run,
    "Email": email.run,
    "LinkedIn": linkedin.run,
    "Reddit": reddit.run,
    "Facebook": facebook.run,
    "X": x_writer.run,
}


def parse_args():
    parser = argparse.ArgumentParser(description="Content Router — Routing Pattern")
    parser.add_argument("--topic", required=True, help="The topic to write content about")
    parser.add_argument("--context", default="", help="Optional context to guide format classification")
    return parser.parse_args()


def stream_step(title: str, generator) -> str:
    """Print a section header then stream the generator output, returning the full text."""
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
    llm = get_llm()

    try:
        # Stage 1: classify
        classification = classifier.run(args.topic, args.context, llm)

        print(f"\n{'=' * 5} STEP 1: Classifying Content Format {'=' * 5}\n")
        print(f"Detected Format: {classification.format}")
        print(f"Reason: {classification.reason}")

        # Stage 2: route to the right writer
        writer_fn = WRITERS.get(classification.format)
        if writer_fn is None:
            print(f"\nError: unrecognised format '{classification.format}'. Expected one of: {list(WRITERS)}")
            sys.exit(1)

        stream_step(
            f"STEP 2: Writing Content for {classification.format}",
            writer_fn(args.topic, args.context, llm),
        )

    except Exception as e:
        print(f"\nError: {e}")
        print("If using Ollama: ensure it is running with `ollama serve`")
        print("If using Anthropic: check your ANTHROPIC_API_KEY in .env")
        sys.exit(1)


if __name__ == "__main__":
    main()

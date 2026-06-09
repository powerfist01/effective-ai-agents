from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import ChatPromptTemplate

from config.llm import get_llm


_prompt = ChatPromptTemplate.from_messages([
    ("human", """You are a LinkedIn content strategist. Write a complete LinkedIn post.

Structure:
- Open with a single bold insight, surprising fact, or counterintuitive statement \
(never start with "I'm excited to share" or "Thrilled to announce")
- Use short paragraphs (1–3 lines each) separated by blank lines for readability on mobile
- Share a personal angle, specific lesson, or concrete observation — not generic advice
- Build toward a practical takeaway or perspective shift the reader didn't have before
- End with a question that invites readers to share their own experience in the comments

Tone: First-person, professional, direct. Thought leadership — not self-promotion.
Length: 150–300 words. Add exactly 3 relevant hashtags on a new line at the very end.

Topic: {topic}
Additional context: {context}"""),
])


def _build_chain(llm):
    return _prompt | llm | StrOutputParser()


def run(topic: str, context: str = "", llm=None):
    if llm is None:
        llm = get_llm()
    return _build_chain(llm).stream({"topic": topic, "context": context or "None provided."})

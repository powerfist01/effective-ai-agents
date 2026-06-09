from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import ChatPromptTemplate

from config.llm import get_llm


_prompt = ChatPromptTemplate.from_messages([
    ("human", """You are an expert email copywriter. Write a complete, ready-to-send email.

Structure:
- Subject: (compelling and specific, under 60 characters — label it "Subject:")
- An opening line that grabs attention and establishes why this matters to the reader
- 2–3 short, scannable paragraphs with the core message — no filler
- A single clear call to action: tell the reader exactly what to do next
- A professional sign-off

Tone: Professional but human. Write like a trusted colleague, not a newsletter blast.
Length: 150–250 words for the body (not counting subject line).

Topic: {topic}
Additional context: {context}"""),
])


def _build_chain(llm):
    return _prompt | llm | StrOutputParser()


def run(topic: str, context: str = "", llm=None):
    if llm is None:
        llm = get_llm()
    return _build_chain(llm).stream({"topic": topic, "context": context or "None provided."})

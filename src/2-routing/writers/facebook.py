from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import ChatPromptTemplate

from config.llm import get_llm


_prompt = ChatPromptTemplate.from_messages([
    ("human", """You are a Facebook content writer. Write a complete, shareable Facebook post.

Structure:
- Open with a warm, relatable hook — a question, a personal observation, \
or a "you know that feeling when..." moment that immediately draws people in
- Use short paragraphs with line breaks — Facebook readers scan, not read
- Include a personal or emotional angle — why does this actually matter to real people in daily life?
- Keep it inclusive and broadly accessible — you're writing for friends, family, and colleagues, \
not just subject-matter experts
- End with a light invitation: ask a question or encourage people to share their own experience

Tone: Warm, conversational, and human. Like sharing something interesting with a group of friends.
Length: 80–150 words.

Topic: {topic}
Additional context: {context}"""),
])


def _build_chain(llm):
    return _prompt | llm | StrOutputParser()


def run(topic: str, context: str = "", llm=None):
    if llm is None:
        llm = get_llm()
    return _build_chain(llm).stream({"topic": topic, "context": context or "None provided."})

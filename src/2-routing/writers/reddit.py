from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import ChatPromptTemplate

from config.llm import get_llm


_prompt = ChatPromptTemplate.from_messages([
    ("human", """You are writing a Reddit post. Write a genuine, community-appropriate post.

Structure:
- Title: Specific and honest — describes exactly what the post is about \
(no clickbait, no "This is incredible!", no vague teases)
- Body: Write like a real person sharing something with people who genuinely care about this topic
- Acknowledge complexity or uncertainty where it exists — Redditors respect nuance and punish oversimplification
- Invite discussion with a genuine question or by sharing what you yourself are still figuring out
- No bullet points of "benefits", no marketing language, no corporate tone

Tone: Casual, genuine, peer-to-peer. Imagine posting in a subreddit full of knowledgeable enthusiasts \
who have seen every corporate post and will call it out.
Length: 100–200 words for the body.

Topic: {topic}
Additional context: {context}"""),
])


def _build_chain(llm):
    return _prompt | llm | StrOutputParser()


def run(topic: str, context: str = "", llm=None):
    if llm is None:
        llm = get_llm()
    return _build_chain(llm).stream({"topic": topic, "context": context or "None provided."})

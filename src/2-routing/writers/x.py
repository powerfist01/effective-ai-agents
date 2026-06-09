from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import ChatPromptTemplate

from config.llm import get_llm


_prompt = ChatPromptTemplate.from_messages([
    ("human", """You are a Twitter/X copywriter. Write a single, standalone tweet.

Rules (all mandatory):
- Maximum 280 characters total including hashtags — count carefully and stay under the limit
- The first 5 words must hook the reader — lead with the most interesting or surprising angle
- Be direct and specific — cut every word that doesn't earn its place
- No thread format — one tweet only, no "1/", no "🧵"
- End with exactly 2–3 relevant hashtags (these count toward your 280 characters)

Tone: Punchy, confident, conversational. Like a smart observation from someone who knows their field — \
not a press release.

Topic: {topic}
Additional context: {context}

Output ONLY the tweet text. No explanation, no "Here's your tweet:", no quotes around it."""),
])


def _build_chain(llm):
    return _prompt | llm | StrOutputParser()


def run(topic: str, context: str = "", llm=None):
    if llm is None:
        llm = get_llm()
    return _build_chain(llm).stream({"topic": topic, "context": context or "None provided."})

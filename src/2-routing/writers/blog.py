from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import ChatPromptTemplate

from config.llm import get_llm


_prompt = ChatPromptTemplate.from_messages([
    ("human", """You are an expert blog writer. Write a complete, publish-ready blog post.

Structure:
- A compelling headline (H1)
- An introduction that hooks the reader and states what they will get from reading
- 3–5 main sections with descriptive H2 headings
- Concrete examples, data points, or analogies in each section
- A conclusion with 3 key takeaways and a call to action

Tone: Informative and authoritative, but accessible. Write for a curious, general technical audience.
Length: 600–900 words.

Topic: {topic}
Additional context: {context}"""),
])


def _build_chain(llm):
    return _prompt | llm | StrOutputParser()


def run(topic: str, context: str = "", llm=None):
    if llm is None:
        llm = get_llm()
    return _build_chain(llm).stream({"topic": topic, "context": context or "None provided."})

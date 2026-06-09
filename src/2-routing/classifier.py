from typing import Literal

from langchain_core.prompts import ChatPromptTemplate
from pydantic import BaseModel

from config.llm import get_llm


class ClassificationResult(BaseModel):
    format: Literal["Blog", "Email", "LinkedIn", "Reddit", "Facebook", "X"]
    reason: str


_prompt = ChatPromptTemplate.from_messages([
    ("human", """You are a content format classifier. Given a topic and optional context, \
choose the single best content format from these six options:

- Blog: Long-form, educational, structured content for readers who want depth
- Email: Direct communication to a specific audience with a clear call to action
- LinkedIn: Professional networking content for career-oriented audiences
- Reddit: Community-driven, conversational content for niche interest groups
- Facebook: Casual social content for broad, mixed audiences
- X: Short, punchy content for real-time conversations and trending topics

Topic: {topic}
Context: {context}

Return the format name exactly as shown above and a one-sentence reason for your choice."""),
])


def run(topic: str, context: str = "", llm=None) -> ClassificationResult:
    if llm is None:
        llm = get_llm()
    chain = _prompt | llm.with_structured_output(ClassificationResult)
    return chain.invoke({"topic": topic, "context": context or "No additional context provided."})

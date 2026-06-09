"""Sentiment analyzer — one section of the parallel analysis.

Returns a typed verdict so the orchestrator can print a clean label like
"[Sentiment] Complete: Positive". Uses LangChain structured output (Pydantic),
mirroring src/2-routing/classifier.py.
"""
from typing import Literal

from langchain_core.prompts import ChatPromptTemplate
from pydantic import BaseModel

from config.llm import get_llm


class SentimentResult(BaseModel):
    verdict: Literal["Positive", "Negative", "Mixed"]
    reason: str  # one sentence justifying the verdict


_prompt = ChatPromptTemplate.from_messages([
    ("human", """You analyze customer reviews. Read the reviews below and decide the OVERALL \
sentiment toward the product.

Choose exactly one verdict:
- Positive: reviews are mostly favorable
- Negative: reviews are mostly unfavorable
- Mixed: reviews are genuinely split or balanced

Give a one-sentence reason grounded in the reviews.

Reviews:
{corpus}"""),
])


async def run(corpus: str, llm=None) -> SentimentResult:
    if llm is None:
        llm = get_llm()
    chain = _prompt | llm.with_structured_output(SentimentResult)
    return await chain.ainvoke({"corpus": corpus})

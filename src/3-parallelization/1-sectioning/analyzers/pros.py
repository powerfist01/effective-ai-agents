"""Pros extractor — one section of the parallel analysis. Returns markdown bullets."""
from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import ChatPromptTemplate

from config.llm import get_llm


_prompt = ChatPromptTemplate.from_messages([
    ("human", """You analyze customer reviews. From the reviews below, extract what people \
CONSISTENTLY LOVE about the product.

Return 3-6 concise markdown bullet points (each starting with "- "). Focus on themes that appear \
across multiple reviews, not one-off opinions. No preamble, just the bullets.

Reviews:
{corpus}"""),
])


async def run(corpus: str, llm=None) -> str:
    if llm is None:
        llm = get_llm()
    chain = _prompt | llm | StrOutputParser()
    return await chain.ainvoke({"corpus": corpus})

"""Target-audience identifier — one section of the parallel analysis. Returns markdown text."""
from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import ChatPromptTemplate

from config.llm import get_llm


_prompt = ChatPromptTemplate.from_messages([
    ("human", """You analyze customer reviews. Based on the reviews below, describe WHO this product \
is best suited for.

Return a short markdown answer: 1-2 sentences naming the ideal user, then 2-4 bullet points of \
specific use-cases or buyer profiles. No preamble.

Reviews:
{corpus}"""),
])


async def run(corpus: str, llm=None) -> str:
    if llm is None:
        llm = get_llm()
    chain = _prompt | llm | StrOutputParser()
    return await chain.ainvoke({"corpus": corpus})

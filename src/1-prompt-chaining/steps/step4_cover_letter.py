from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import ChatPromptTemplate

from config.llm import get_llm

_prompt = ChatPromptTemplate.from_messages([
    ("human", """You are an expert cover letter writer. Using the job description and gap analysis \
below, write a compelling, personalized cover letter. The letter should:
- Open with a strong hook connecting the candidate to this specific role
- Directly address the key requirements from the JD
- Reframe any gaps as growth areas or transferable skills
- Close confidently with a clear call to action
- Be 3-4 paragraphs, professional but not stiff

---
Job Description:
{structured_jd}

---
Gap Analysis:
{gap_analysis}"""),
])


def _build_chain(llm):
    return _prompt | llm | StrOutputParser()


def run(structured_jd: str, gap_analysis: str, llm=None):
    if llm is None:
        llm = get_llm()
    return _build_chain(llm).stream({"structured_jd": structured_jd, "gap_analysis": gap_analysis})

from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import ChatPromptTemplate

from config.llm import get_llm

_prompt = ChatPromptTemplate.from_messages([
    ("human", """You are a career advisor. Compare the job description and resume below and \
produce a gap analysis with three sections:

## Strong Matches
Skills, experience, and qualifications the candidate clearly has.

## Gaps & Weaknesses
Requirements in the JD that the candidate lacks or only partially meets.

## Areas to Address
Specific points the candidate should highlight or explain in their application to bridge the gaps.

---
Job Description:
{structured_jd}

---
Resume:
{resume_text}"""),
])


def _build_chain(llm):
    return _prompt | llm | StrOutputParser()


def run(structured_jd: str, resume_text: str, llm=None):
    if llm is None:
        llm = get_llm()
    return _build_chain(llm).stream({"structured_jd": structured_jd, "resume_text": resume_text})

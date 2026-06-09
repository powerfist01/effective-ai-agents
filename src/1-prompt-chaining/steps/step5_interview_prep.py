from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import ChatPromptTemplate

from config.llm import get_llm

_prompt = ChatPromptTemplate.from_messages([
    ("human", """You are an interview coach. Based on the job description, resume, and gap analysis \
below, generate 10 likely interview questions the candidate should prepare for. For each question:
1. State the question
2. Explain in one sentence why the interviewer would ask it
3. List 2-3 key points to hit in the answer given the candidate's specific profile and gaps

---
Job Description:
{structured_jd}

---
Resume:
{resume_text}

---
Gap Analysis:
{gap_analysis}"""),
])


def _build_chain(llm):
    return _prompt | llm | StrOutputParser()


def run(structured_jd: str, resume_text: str, gap_analysis: str, llm=None):
    if llm is None:
        llm = get_llm()
    return _build_chain(llm).stream({
        "structured_jd": structured_jd,
        "resume_text": resume_text,
        "gap_analysis": gap_analysis,
    })

from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import ChatPromptTemplate

from config.llm import get_llm

_prompt = ChatPromptTemplate.from_messages([
    ("human", """You are a job description formatter. Take the raw job description below and \
    reformat it into clean, well-structured Markdown with these sections: Job Title, Company Overview, \
    Role Summary, Key Responsibilities, Required Qualifications, Nice-to-Have Qualifications, and \
    Compensation & Benefits (only if mentioned). Preserve all information — do not summarize or omit details.

    Raw Job Description:
    {jd_raw}"""),
])


def _build_chain(llm):
    return _prompt | llm | StrOutputParser()


def run(jd_raw: str, llm=None):
    if llm is None:
        llm = get_llm()
    return _build_chain(llm).stream({"jd_raw": jd_raw})

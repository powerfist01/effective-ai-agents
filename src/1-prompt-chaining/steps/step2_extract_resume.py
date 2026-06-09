from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import ChatPromptTemplate

from config.llm import get_llm

_prompt = ChatPromptTemplate.from_messages([
    ("human", """You are a resume text cleaner. The text below was extracted from a PDF and may \
contain OCR artifacts, irregular spacing, or formatting issues. Clean it into readable, \
well-structured plain text preserving all information: contact details, work experience, \
education, skills, and other sections. Fix spacing and line breaks only — do not add, remove, \
or change any factual content. If the text is empty or clearly unreadable, say so explicitly.

Raw Extracted Resume Text:
{resume_raw}"""),
])


def _build_chain(llm):
    return _prompt | llm | StrOutputParser()


def run(resume_raw: str, llm=None):
    if llm is None:
        llm = get_llm()
    return _build_chain(llm).stream({"resume_raw": resume_raw})

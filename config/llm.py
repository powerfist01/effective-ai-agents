import os

from langchain_anthropic import ChatAnthropic
from langchain_ollama import ChatOllama


def get_llm():
    api_key = os.getenv("ANTHROPIC_API_KEY")
    if api_key:
        return ChatAnthropic(model_name="claude-sonnet-4-6", api_key=api_key, timeout=180, max_retries=3, stop=["\n\nHuman:", "\n\nAssistant:"])

    model = os.getenv("OLLAMA_MODEL", "gemma4:26b")
    base_url = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")

    return ChatOllama(model=model, base_url=base_url)

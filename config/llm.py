"""
LLM client for AITUNNEL (OpenAI-compatible API).
Uses AITUNNEL_API_KEY, AITUNNEL_BASE_URL, AITUNNEL_MODEL from environment.
"""
import os

from langchain_openai import ChatOpenAI

AITUNNEL_BASE_URL = os.getenv("AITUNNEL_BASE_URL", "https://api.aitunnel.ru/v1/")
AITUNNEL_API_KEY = os.getenv("AITUNNEL_API_KEY", "")
AITUNNEL_MODEL = os.getenv("AITUNNEL_MODEL", "deepseek-r1")


def get_llm(
    model: str | None = None,
    temperature: float = 0.4,
    max_tokens: int = 50000,
) -> ChatOpenAI:
    """
    Return ChatOpenAI client configured for AITUNNEL.
    api_key and base_url from AITUNNEL_API_KEY, AITUNNEL_BASE_URL.
    """
    return ChatOpenAI(
        api_key=AITUNNEL_API_KEY or os.getenv("OPENAI_API_KEY"),
        base_url=AITUNNEL_BASE_URL,
        model=model or AITUNNEL_MODEL,
        temperature=temperature,
        max_tokens=max_tokens,
    )

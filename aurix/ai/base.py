"""LLM provider abstraction for AURIX."""

import os
from typing import Optional


class LLMProvider:
    """Wraps LangChain ChatGroq as the single LLM backend."""

    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key or os.getenv("GROQ_API_KEY")
        if not self.api_key:
            raise ValueError("GROQ_API_KEY not provided")
        self._llm = None

    @property
    def llm(self):
        """Lazy-initialize ChatGroq instance."""
        if self._llm is None:
            from langchain_groq import ChatGroq
            self._llm = ChatGroq(
                model="llama-3.3-70b-versatile",
                temperature=0.3,
                max_tokens=1024,
                api_key=self.api_key,
            )
        return self._llm

    def invoke(self, messages: list, max_tokens: int = 1024) -> str:
        """Invoke LLM with message list, return content string."""
        from langchain_core.messages import SystemMessage, HumanMessage
        lc_messages = []
        for msg in messages:
            if msg["role"] == "system":
                lc_messages.append(SystemMessage(content=msg["content"]))
            else:
                lc_messages.append(HumanMessage(content=msg["content"]))
        result = self.llm.invoke(lc_messages, max_tokens=max_tokens)
        return result.content

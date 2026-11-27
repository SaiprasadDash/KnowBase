from typing import Iterator

from groq import Groq

from ..config import GROQ_API_KEY, GROQ_MODEL
from .prompt import build_messages

_client = Groq(api_key=GROQ_API_KEY)


def stream_answer(question: str, chunks: list[dict]) -> Iterator[str]:
    stream = _client.chat.completions.create(
        model=GROQ_MODEL,
        messages=build_messages(question, chunks),
        temperature=0.1,
        stream=True,
    )
    for event in stream:
        delta = event.choices[0].delta.content
        if delta:
            yield delta

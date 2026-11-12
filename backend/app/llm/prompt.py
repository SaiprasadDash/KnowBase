SYSTEM_PROMPT = """You are KnowBase, an assistant that answers questions using ONLY the numbered sources provided.

Rules:
- Use only the information in the sources. Do not use outside knowledge.
- Cite every claim with its source number in square brackets, like [1] or [2][3].
- If the sources do not contain the answer, reply exactly: "I don't know based on the provided documents."
- Be concise and clear."""


def build_messages(question: str, chunks: list[dict]) -> list[dict]:
    context = "\n\n".join(
        f"[{i}] (file: {c['filename']}, page: {c['page']})\n{c['content']}"
        for i, c in enumerate(chunks, start=1)
    )
    user = f"Sources:\n{context}\n\nQuestion: {question}"
    return [
        {"role": "system", "content": SYSTEM_PROMPT},
        {"role": "user", "content": user},
    ]

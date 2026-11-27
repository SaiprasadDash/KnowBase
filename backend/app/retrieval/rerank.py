from sentence_transformers import CrossEncoder

_reranker = CrossEncoder("BAAI/bge-reranker-base")


def rerank(query: str, chunks: list[dict], top_k: int = 5) -> list[dict]:
    if not chunks:
        return []
    scores = _reranker.predict([(query, c["content"]) for c in chunks])
    for c, s in zip(chunks, scores):
        c["score"] = float(s)
    return sorted(chunks, key=lambda c: c["score"], reverse=True)[:top_k]

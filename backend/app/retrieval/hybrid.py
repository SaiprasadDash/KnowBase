import re

import numpy as np

from ..db import get_conn
from ..ingest.embed import embed_query

COLS = "c.id, c.content, c.page, c.heading, d.filename"


def _row_to_dict(r) -> dict:
    return {"id": r[0], "content": r[1], "page": r[2], "heading": r[3], "filename": r[4]}


def vector_search(conn, query: str, k: int = 20) -> list[dict]:
    qvec = np.array(embed_query(query))
    rows = conn.execute(
        f"SELECT {COLS} FROM chunks c JOIN documents d ON d.id = c.document_id "
        "ORDER BY c.embedding <=> %s LIMIT %s",
        (qvec, k),
    ).fetchall()
    return [_row_to_dict(r) for r in rows]


def keyword_search(conn, query: str, k: int = 20) -> list[dict]:
    words = re.findall(r"\w+", query)
    if not words:
        return []
    tsq = " | ".join(words)  # OR match, ranked by ts_rank
    rows = conn.execute(
        f"SELECT {COLS} FROM chunks c JOIN documents d ON d.id = c.document_id "
        "WHERE c.tsv @@ to_tsquery('english', %s) "
        "ORDER BY ts_rank(c.tsv, to_tsquery('english', %s)) DESC LIMIT %s",
        (tsq, tsq, k),
    ).fetchall()
    return [_row_to_dict(r) for r in rows]


def rrf_merge(lists: list[list[dict]], k: int = 60) -> list[dict]:
    """Reciprocal Rank Fusion: combine several ranked lists into one."""
    scores: dict[int, float] = {}
    items: dict[int, dict] = {}
    for lst in lists:
        for rank, item in enumerate(lst):
            scores[item["id"]] = scores.get(item["id"], 0.0) + 1.0 / (k + rank + 1)
            items[item["id"]] = item
    ordered = sorted(scores, key=scores.get, reverse=True)
    return [items[i] for i in ordered]


def hybrid_search(query: str, k: int = 20) -> list[dict]:
    with get_conn() as conn:
        vec = vector_search(conn, query, k)
        kw = keyword_search(conn, query, k)
    return rrf_merge([vec, kw])[:k]

import numpy as np

from ..db import get_conn
from .chunk import chunk_pages
from .embed import embed_documents
from .parse import parse_file


def ingest(filename: str, data: bytes) -> dict:
    pages = parse_file(filename, data)
    chunks = chunk_pages(pages)
    if not chunks:
        raise ValueError("No text could be extracted from this file")

    vectors = embed_documents([c["content"] for c in chunks])

    with get_conn() as conn:
        doc_id = conn.execute(
            "INSERT INTO documents (filename) VALUES (%s) RETURNING id", (filename,)
        ).fetchone()[0]
        for c, v in zip(chunks, vectors):
            conn.execute(
                "INSERT INTO chunks (document_id, content, page, heading, embedding) "
                "VALUES (%s, %s, %s, %s, %s)",
                (doc_id, c["content"], c["page"], c["heading"], np.array(v)),
            )
    return {"document_id": doc_id, "filename": filename, "chunks": len(chunks)}

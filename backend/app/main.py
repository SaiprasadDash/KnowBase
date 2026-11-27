import json

from fastapi import FastAPI, File, HTTPException, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse
from pydantic import BaseModel

from .db import get_conn, init_db
from .ingest.pipeline import ingest
from .llm.answer import stream_answer
from .retrieval.hybrid import hybrid_search
from .retrieval.rerank import rerank

app = FastAPI(title="KnowBase API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.on_event("startup")
def startup() -> None:
    init_db()


class ChatRequest(BaseModel):
    question: str


@app.get("/health")
def health():
    return {"status": "ok"}


@app.post("/upload")
async def upload(file: UploadFile = File(...)):
    data = await file.read()
    try:
        return ingest(file.filename, data)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@app.get("/documents")
def list_documents():
    with get_conn() as conn:
        rows = conn.execute(
            "SELECT d.id, d.filename, d.uploaded_at, COUNT(c.id) "
            "FROM documents d LEFT JOIN chunks c ON c.document_id = d.id "
            "GROUP BY d.id ORDER BY d.id DESC"
        ).fetchall()
    return [
        {"id": r[0], "filename": r[1], "uploaded_at": r[2].isoformat(), "chunks": r[3]}
        for r in rows
    ]


@app.delete("/documents/{doc_id}")
def delete_document(doc_id: int):
    with get_conn() as conn:
        conn.execute("DELETE FROM documents WHERE id = %s", (doc_id,))
    return {"deleted": doc_id}


def _sse(payload: dict) -> str:
    return f"data: {json.dumps(payload)}\n\n"


@app.post("/chat")
def chat(req: ChatRequest):
    question = req.question.strip()
    if not question:
        raise HTTPException(status_code=400, detail="Question is empty")

    candidates = hybrid_search(question, k=20)
    top = rerank(question, candidates, top_k=5)

    def event_stream():
        sources = [
            {
                "n": i,
                "filename": c["filename"],
                "page": c["page"],
                "heading": c["heading"],
                "snippet": c["content"][:300],
            }
            for i, c in enumerate(top, start=1)
        ]
        yield _sse({"type": "sources", "sources": sources})
        if not top:
            yield _sse({"type": "token", "text": "I don't know based on the provided documents."})
        else:
            for token in stream_answer(question, top):
                yield _sse({"type": "token", "text": token})
        yield _sse({"type": "done"})

    return StreamingResponse(event_stream(), media_type="text/event-stream")

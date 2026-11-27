from sentence_transformers import SentenceTransformer

_model = SentenceTransformer("BAAI/bge-small-en-v1.5")


def embed_documents(texts: list[str]) -> list[list[float]]:
    return _model.encode(
        texts, normalize_embeddings=True, batch_size=32, show_progress_bar=False
    ).tolist()


def embed_query(query: str) -> list[float]:
    # BGE needs this prefix for queries only, not for documents
    prefix = "Represent this sentence for searching relevant passages: "
    return _model.encode(prefix + query, normalize_embeddings=True).tolist()

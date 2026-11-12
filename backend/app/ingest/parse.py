import fitz  # PyMuPDF


def parse_file(filename: str, data: bytes) -> list[dict]:
    """Return a list of {"page": int, "text": str}."""
    name = filename.lower()
    if name.endswith(".pdf"):
        doc = fitz.open(stream=data, filetype="pdf")
        pages = []
        for i, page in enumerate(doc):
            text = page.get_text()
            if text.strip():
                pages.append({"page": i + 1, "text": text})
        return pages
    if name.endswith((".md", ".txt")):
        return [{"page": 1, "text": data.decode("utf-8", errors="ignore")}]
    raise ValueError("Only .pdf, .md and .txt files are supported")

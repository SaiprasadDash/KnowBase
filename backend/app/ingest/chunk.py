import re


def chunk_pages(pages: list[dict], size: int = 1500, overlap: int = 200) -> list[dict]:
    """Split pages into ~size-character chunks, keeping page number and last seen heading."""
    chunks: list[dict] = []
    heading = None

    for p in pages:
        buf = ""
        for para in re.split(r"\n\s*\n", p["text"]):
            para = para.strip()
            if not para:
                continue
            m = re.match(r"^#{1,6}\s+(.*)", para)
            if m:
                heading = m.group(1).strip()
            if buf and len(buf) + len(para) > size:
                chunks.append({"content": buf.strip(), "page": p["page"], "heading": heading})
                buf = buf[-overlap:]
            buf += "\n\n" + para
        if buf.strip():
            chunks.append({"content": buf.strip(), "page": p["page"], "heading": heading})

    return chunks

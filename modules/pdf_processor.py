import fitz

def extract_pdf(data: bytes):
    """Return (combined_text, page_count), preserving page boundaries."""
    if not data or not data.startswith(b"%PDF"):
        raise ValueError("The uploaded file is not a valid PDF.")
    doc = fitz.open(stream=data, filetype="pdf")
    pages=[]
    for i, page in enumerate(doc):
        text=page.get_text("text").strip()
        if text:
            pages.append(f"[PAGE {i+1}]\n{text}")
    count=len(doc)
    doc.close()
    return "\n\n".join(pages), count

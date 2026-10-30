from modules.rag_engine import DocumentStore

def test_split_preserves_source_and_page():
    store=DocumentStore()
    chunks=store._split("[PAGE 1]\nHello contract. [PAGE 2]\nPayment terms.", "demo.pdf")
    assert len(chunks)==2
    assert chunks[0]["page"]==1
    assert chunks[1]["page"]==2
    assert all(c["source"]=="demo.pdf" for c in chunks)

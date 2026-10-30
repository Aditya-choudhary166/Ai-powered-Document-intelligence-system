import re
import numpy as np
import faiss
from sentence_transformers import SentenceTransformer
from config.settings import EMBEDDING_MODEL, CHUNK_SIZE, CHUNK_OVERLAP

class DocumentStore:
    def __init__(self):
        self.model=None
        self.index=None
        self.chunks=[]

    def _model(self):
        if self.model is None:
            self.model=SentenceTransformer(EMBEDDING_MODEL)
        return self.model

    def _split(self, text, source):
        out=[]
        # Split on explicit page markers, then chunk within each page to preserve citations.
        pages=re.split(r"\\[PAGE (\\d+)\\]", text)
        for i in range(1,len(pages),2):
            page_no=int(pages[i]); body=pages[i+1].strip()
            start=0
            while start < len(body):
                end=min(start+CHUNK_SIZE,len(body))
                piece=body[start:end].strip()
                if piece: out.append({"text":piece,"source":source,"page":page_no})
                if end==len(body): break
                start=max(0,end-CHUNK_OVERLAP)
        return out

    def build(self, documents):
        self.chunks=[]
        for d in documents: self.chunks.extend(self._split(d["text"],d["name"]))
        if not self.chunks: raise ValueError("No text chunks were available to index.")
        vectors=self._model().encode([c["text"] for c in self.chunks], normalize_embeddings=True, show_progress_bar=False)
        vectors=np.asarray(vectors,dtype="float32")
        self.index=faiss.IndexFlatIP(vectors.shape[1])
        self.index.add(vectors)

    def search(self, query, k=5):
        if self.index is None: return []
        q=self._model().encode([query],normalize_embeddings=True)
        scores, ids=self.index.search(np.asarray(q,dtype="float32"), min(k,len(self.chunks)))
        return [{**self.chunks[int(i)],"score":float(s)} for s,i in zip(scores[0],ids[0]) if i>=0]

import json
import requests
from config.settings import GROQ_API_KEY, GROQ_MODEL, GROQ_BASE_URL

SYSTEM = """You are a careful business document analyst. Use only supplied document text.
Never invent facts, dates, clauses, or page references. If evidence is missing, say so.
Treat findings as preliminary business observations, not legal advice."""

class AIEngine:
    def __init__(self):
        self.api_key=GROQ_API_KEY

    def _chat(self, messages, temperature=0.1):
        if not self.api_key: raise RuntimeError("GROQ_API_KEY is missing. Add it to .env.")
        payload={"model":GROQ_MODEL,"messages":[{"role":"system","content":SYSTEM},*messages],
                 "temperature":temperature}
        r=requests.post(GROQ_BASE_URL,headers={"Authorization":f"Bearer {self.api_key}","Content-Type":"application/json"},
                        json=payload,timeout=90)
        if not r.ok:
            raise RuntimeError(f"Groq API error ({r.status_code}): {r.text[:500]}")
        return r.json()["choices"][0]["message"]["content"]

    @staticmethod
    def _json(text):
        cleaned=text.strip()
        if cleaned.startswith("```"):
            cleaned=cleaned.split("\n",1)[-1].rsplit("```",1)[0].strip()
        start=cleaned.find("{"); end=cleaned.rfind("}")
        if start<0 or end<start: raise ValueError("The AI did not return valid JSON. Please retry.")
        return json.loads(cleaned[start:end+1])

    def analyze(self, documents):
        # Bound context to keep requests reliable; long documents are represented by excerpts.
        context="\n\n".join(f"SOURCE: {d['name']}\n{d['text'][:12000]}" for d in documents)
        prompt=f"""Analyze these business documents. Return ONLY valid JSON with keys:
summary (string), key_information (array of strings),
risks (array of objects with title, level [High/Medium/Low], description, evidence, source, page),
actions (array of objects with task, owner, deadline, priority).
For each risk use a page number only if explicit page markers support it. Do not infer missing clauses.
DOCUMENTS:\n{context[:26000]}"""
        return self._json(self._chat([{"role":"user","content":prompt}]))

    def answer(self, question, chunks):
        context="\n\n".join(f"SOURCE: {c['source']} | PAGE: {c['page']}\n{c['text']}" for c in chunks)
        prompt=f"""Answer the question using only the context. Cite sources inline as [filename, page N].
If the answer is not present, say: "I could not find this information in the uploaded documents."
QUESTION: {question}\nCONTEXT:\n{context}"""
        return self._chat([{"role":"user","content":prompt}])

# AI-Powered Document Intelligence & Business Automation Agent

A Streamlit application for PDF extraction, semantic retrieval (RAG), grounded document Q&A, AI summaries, potential contract risk identification, action-item extraction, and PDF reporting.

## Requirements
- Python 3.10 or 3.11 recommended
- Groq API key (for LLM analysis and chat)
- Internet connection on first run to download the Sentence Transformers embedding model

## Setup
```bash
python -m venv .venv
# Windows:
.venv\Scripts\activate
# macOS/Linux:
source .venv/bin/activate
pip install -r requirements.txt
```

Copy `.env.example` to `.env` and add your Groq API key:
```env
GROQ_API_KEY=your_actual_key
GROQ_MODEL=llama-3.3-70b-versatile
```

Run:
```bash
streamlit run app.py
```

## Workflow
1. Open **Document Analysis** and upload text-based PDF files.
2. Click **Process uploaded PDFs** to extract text and build the FAISS index.
3. Click **Run full AI analysis** for summary, key information, potential risks, and action items.
4. Use **AI Chat** to ask questions with retrieved document source/page context.
5. Download a report from **Reports**.

A sample synthetic service agreement is available in `sample_documents/`.

## Notes
- Scanned PDFs need OCR; OCR is not included in this MVP.
- Embedding model downloads on first run and runs locally afterwards.
- Groq is used for generation; keep your API key private and never commit `.env`.
- AI findings are preliminary and must be reviewed by a human. This is not legal advice.
- Uploaded documents are held in the Streamlit session and are not intentionally persisted by this app.

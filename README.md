# 🌸 Kohler Unified Enterprise AI Agent

> A soft rose-gold case-study prototype for a multi-domain enterprise AI assistant.

The Kohler Unified Enterprise AI Agent answers questions across **HR Policy**, **Customer Support**, **Privacy Policy**, **Financial Guidelines**, and **Legal / Compliance**. It demonstrates domain-aware routing, local retrieval, governed generation, dynamic response formatting, and live grounding checks in a simple Streamlit chat experience.

## ✦ Architecture Vision

The full production vision is a multi-agent conversational system:

```text
User message + conversation history
              ↓
      Orchestrator / router
              ↓
     Gemini domain classifier
              ↓
 ┌────────────┼────────────┐
 HR RAG     Support RAG   Privacy RAG
 Financial RAG             Legal / Compliance RAG
              ↓
      Grounded Gemini answer
              ↓
       Output formatter
              ↓
 Live faithfulness check + JSONL observability log
              ↓
          Streamlit chat UI
```

The production architecture is designed to support independent domain specialists, strict data governance, persistent conversation history, stronger evaluation, and additional enterprise integrations without fine-tuning the model.

## ✿ Prototype Scope

Implemented in this case-study prototype:

- Five local document domains with separate ChromaDB collections:
  - `hr_policy`
  - `customer_support`
  - `privacy_policy`
        - `financial_guidelines`
        - `legal_compliance`
- Plain Python document loading and overlapping word-based chunking
- `sentence-transformers` embeddings using `all-MiniLM-L6-v2`
- Local persistent ChromaDB storage in `chroma_db/`
- Gemini-powered context-aware domain classification using recent conversation history
- Retrieval of up to four ranked chunks from the selected domain
- Orchestrated answer generation with sensitive-data governance instructions
- Output detection and formatting for markdown, email, and JSON
- A second Gemini call for live faithfulness checking
- Local JSONL faithfulness logging
- Minimal single-page Streamlit chat UI with pink styling and session-backed history

Still part of the longer production vision:

- Independent deployable specialist agents and service boundaries
- Authentication, authorization, secrets management, and enterprise observability
- Production vector storage, document ingestion pipelines, and policy versioning
- Robust automated test coverage and monitoring dashboards
- Offline `ragas` evaluation workflow and larger domain-specific evaluation sets
- Human review workflows for sensitive or low-confidence responses

## 🧰 Tech Stack

| Layer | Technology |
| --- | --- |
| Language | Python 3.11 |
| LLM API | Google Gemini via `google-genai` |
| Embeddings | `sentence-transformers` with `all-MiniLM-L6-v2` |
| Vector database | Local ChromaDB |
| UI | Streamlit |
| Evaluation | `ragas` (offline evaluation foundation) |
| Configuration | `python-dotenv` and `.env` |

No LangChain is used. Retrieval is implemented directly in Python for transparency and easier debugging.

## 🌷 Setup

### 1. Clone the repository

```bash
git clone <your-repository-url>
cd ai_project
```

### 2. Create and activate a Python 3.11 virtual environment

Windows PowerShell:

```powershell
py -3.11 -m venv venv
.\venv\Scripts\Activate.ps1
```

macOS/Linux:

```bash
python3.11 -m venv venv
source venv/bin/activate
```

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

### 4. Configure Gemini

Copy `.env.example` to `.env` and add your Gemini API key:

```powershell
Copy-Item .env.example .env
```

Then edit `.env`:

```env
GEMINI_API_KEY=your_real_gemini_api_key
```

Never commit `.env` or expose the API key. It is excluded by `.gitignore`.

### 5. Build local embeddings and ChromaDB storage

```bash
python build_vector_store.py
```

This loads the sample `.txt` files, creates embeddings, and writes three local collections under `chroma_db/`.

### 6. Run the Streamlit app

```bash
streamlit run app.py
```

Open the local URL shown by Streamlit, usually `http://localhost:8501`.

## 💗 Demo

Try questions from each domain:

- **HR:** “How many leave days do I get?”
- **Customer Support:** “What is your return policy?”
- **Privacy:** “How is my data used?”
- **Financial Guidelines:** “What expenses can employees claim?”
- **Legal / Compliance:** “What are our compliance obligations?”

The classifier uses the current message and recent conversation context, so it can follow a topic and detect when the user switches domains. The UI displays the routed domain, retrieves the relevant local policy chunks, and generates a grounded answer.

You can also request a response format directly:

- Ask for **JSON** to receive `answer`, `source_domain`, and `confidence`
- Ask for an **email** to receive a concise professional email wrapper
- Ask for **Excel**, **CSV**, or a **download** to receive a downloadable CSV file containing the answer, source domain, and confidence
- Ask for **XML** to receive a structured `<response>` document
- Otherwise, receive normal **markdown** conversation text

After each answer, a separate Gemini grounding check records whether the answer is supported by the retrieved context in `faithfulness_log.jsonl`.

Sensitive customer data is governed by the orchestrator and evaluator instructions: the system refuses direct requests to expose names, account numbers, contact details, or other identifying information.

## 📁 Key Files

- `app.py` — pink Streamlit chat UI
- `orchestrator.py` — routing, grounded generation, and governance
- `domain_classifier.py` — context-aware Gemini domain classification
- `retriever.py` — domain-scoped Chroma retrieval
- `vector_store.py` — embeddings and local ChromaDB persistence
- `build_vector_store.py` — CLI entry point for local indexing
- `output_formatter.py` — markdown, email, and JSON output formatting
- `faithfulness.py` — live grounding check and JSONL logging
- `data/` — sample policy documents by domain

## 🌹 Notes

This repository is a solo case-study prototype intended for local development and demonstration. The local `chroma_db/`, `.env`, virtual environment, Python caches, and JSONL logs are ignored from version control.
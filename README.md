# 🚀 Production-Ready-RAG

A production-oriented Retrieval-Augmented Generation (RAG) application built using FastAPI, Streamlit, Inngest, Qdrant, OpenAI, and LlamaIndex.

This project allows users to upload PDF documents, automatically chunk and embed their content, store embeddings in a vector database, and perform intelligent question-answering over the uploaded documents using Retrieval-Augmented Generation.

---

## ✨ Features

* 📄 PDF document ingestion
* ✂️ Automatic document chunking
* 🧠 Semantic embeddings generation
* 🗂️ Vector storage using Qdrant
* 🔍 Context-aware semantic search
* 🤖 AI-powered question answering
* ⚡ Event-driven workflows using Inngest
* 🌐 FastAPI backend services
* 🎨 Interactive Streamlit frontend
* 🔄 Asynchronous processing pipeline
* 📚 Source attribution support

---

# 🏗️ System Architecture

```text
PDF Upload
    │
    ▼
LlamaIndex PDF Reader
    │
    ▼
Sentence Splitter
    │
    ▼
OpenAI Embeddings
    │
    ▼
Qdrant Vector Database
    │
    ▼
Semantic Retrieval
    │
    ▼
GPT-4o-mini
    │
    ▼
Final Answer + Sources
```

---

# 🛠️ Technologies Used

## Backend

* FastAPI
* Python
* Uvicorn

## Workflow Orchestration

* Inngest
* Inngest AI Workflows

## AI & LLM

* OpenAI API
* GPT-4o-mini
* OpenAI Embeddings
* Retrieval-Augmented Generation (RAG)

## Vector Database

* Qdrant
* Qdrant Client

## Document Processing

* LlamaIndex
* PDFReader
* SentenceSplitter

## Frontend

* Streamlit

## Environment Management

* UV Package Manager
* Python Virtual Environment
* dotenv

## Containerization

* Docker
* Docker Desktop

---

# 📂 Project Structure

```text
Production-Ready-RAG/
│
├── main.py
├── data_loader.py
├── vector_db.py
├── custom_types.py
├── streamlit_app.py
├── .env
├── pyproject.toml
├── uv.lock
│
├── uploaded_pdfs/
│
└── README.md
```

---

# ⚙️ Installation

## Clone Repository

```bash
git clone https://github.com/YeshwanthK172/Production-Ready-RAG.git
cd Production-Ready-RAG
```

## Create Environment

```bash
uv venv
```

Activate environment:

### Windows

```powershell
.venv\Scripts\activate
```

### Linux / Mac

```bash
source .venv/bin/activate
```

## Install Dependencies

```bash
uv sync
```

---

# 🔑 Environment Variables

Create a `.env` file.

```env
OPENAI_API_KEY=your_openai_api_key
```

---

# 🐳 Start Qdrant

```bash
docker run -d \
--name qdrant \
-p 6333:6333 \
qdrant/qdrant
```

Verify:

```bash
http://localhost:6333/dashboard
```

---

# 🚀 Run FastAPI

```bash
uv run uvicorn main:app --reload
```

Backend:

```text
http://127.0.0.1:8000
```

---

# ⚡ Run Inngest Dev Server

```bash
npx inngest-cli@latest dev
```

Dashboard:

```text
http://localhost:8288
```

---

# 🎨 Run Streamlit

```bash
streamlit run streamlit_app.py
```

Frontend:

```text
http://localhost:8501
```

---

# 🔄 RAG Workflow

### Document Ingestion

1. Upload PDF
2. Extract text
3. Chunk content
4. Generate embeddings
5. Store vectors in Qdrant

### Query Processing

1. User asks question
2. Generate query embedding
3. Search similar chunks in Qdrant
4. Retrieve relevant context
5. Send context to GPT-4o-mini
6. Generate final answer
7. Return sources

---

# 📊 Core Components

| Component         | Purpose                  |
| ----------------- | ------------------------ |
| FastAPI           | Backend API              |
| Streamlit         | User Interface           |
| Inngest           | Event Workflows          |
| Qdrant            | Vector Database          |
| OpenAI Embeddings | Semantic Vector Creation |
| GPT-4o-mini       | Answer Generation        |
| LlamaIndex        | PDF Processing           |

---

# 🎯 Future Enhancements

* Multi-document support
* Citation highlighting
* Hybrid search
* Reranking models
* Local embeddings support
* Multi-user authentication
* Cloud deployment
* Chat history persistence

---

# 👨‍💻 Author

**Yeshwanth K**

GitHub:
https://github.com/YeshwanthK172

---

# ⭐ Support

If you found this project useful, consider giving it a star on GitHub.

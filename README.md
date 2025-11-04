# 📚 Legal RAG Assistant (FastAPI + Streamlit + Pinecone + Groq)

A Retrieval-Augmented Generation (RAG) based legal assistant that allows you to:

✅ Upload documents (PDF/TXT)  
✅ Store & embed them into Pinecone  
✅ Ask legal questions using natural language  
✅ Get responses powered by Groq LLM + document context  

---

## 🚀 Tech Stack

| Layer | Tech |
|-------|------|
| Backend API | FastAPI |
| Frontend UI | Streamlit |
| Vector DB | Pinecone |
| Embeddings | SentenceTransformer (`all-MiniLM-L6-v2`) |
| LLM Inference | Groq API |
| File Parsing | pypdf / txt |
| Environment | Python 3.9+ |

---

## 🔧 1. Setup & Installation

### 1️⃣ Clone repo & enter project

git clone https://github.com/uzairabbasi989/RAG

cd project

2️⃣ Create Virtual Environment

python -m venv venv

source venv/bin/activate       # Mac/Linux

venv\Scripts\activate          # Windows

3️⃣ Install dependencies

pip install -r requirements.txt

4️⃣ Create .env file

PINECONE_API_KEY=your_key_here

GROQ_API_KEY=your_key_here

INDEX_NAME=legal-index

🗂️ 2. Run Backend (FastAPI)

uvicorn main:app --reload

Backend will run at:

➡️ http://127.0.0.1:8000

API Docs available at:

➡️ http://127.0.0.1:8000/docs

💻 3. Run Frontend (Streamlit)

streamlit run frontend.py

Frontend will open in browser automatically.

Used for:

Uploading documents

Asking questions

Chat-like Q/A interface

📤 4. Upload Documents

You can upload .pdf or .txt files directly from the Streamlit UI.

The system will:

✅ Read content
✅ Chunk text
✅ Generate embeddings
✅ Store vectors in Pinecone

No manual ingestion script is required.

💬 5. Ask Questions

You can query documents in two ways:

✅ Using Streamlit UI (recommended)
Open the web UI and chat.

✅ Using API directly:

curl "http://127.0.0.1:8000/ask?query=What is termination clause?"

📁 Project Structure

project/
│ backend.py               # FastAPI backend
│ frontend.py           # Streamlit UI
│ requirements.txt
│ README.md
| .gitignore
│ .env
│
└── documents/          # (optional) local storage

🔄 Workflow Summary
markdown

1. Upload documents via Streamlit
2. System embeds and stores chunks in Pinecone
3. User enters question
4. System retrieves relevant chunks
5. Sends context + question to Groq LLM
6. Returns answer with cited sources
7. 
✅ TODO (future improvements)
 Doc duplicate detection via hashing

 Add support for DOCX + HTML

 "Delete document" API

 PDF OCR for scanned files

 Streamed responses

🛠 Troubleshooting
Issue	Fix
Backend not responding	Make sure FastAPI is running
Pinecone errors	Check .env API key & index name
No answer returned	Ensure some docs are uploaded first
CORS blocked	Use --reload or enable CORS in FastAPI

📜 License
MIT — feel free to use, modify, distribute.

✨ Author
Made by uzair using Groq + Pinecone + FastAPI + Streamlit

from typing import List
from fastapi import FastAPI, UploadFile, File
from fastapi.responses import JSONResponse
import os
import uuid
from pypdf import PdfReader
from sentence_transformers import SentenceTransformer
from pinecone import Pinecone, ServerlessSpec
from groq import Groq
from dotenv import load_dotenv

load_dotenv()

# -----------------------------
# INIT
# -----------------------------
model = SentenceTransformer("all-MiniLM-L6-v2")  # 384-dim
pc = Pinecone(api_key=os.getenv("PINECONE_API_KEY"))
groq_client = Groq(api_key=os.getenv("YOUR_GROQ_KEY"))
index_name = "legal-rag"

# Create index if not exists
if index_name not in pc.list_indexes().names():
    pc.create_index(
        name=index_name,
        dimension=384,
        metric="cosine",
        spec=ServerlessSpec(
            cloud="aws",
            region="us-east-1"
        )
    )

index = pc.Index(index_name)
app = FastAPI()

# -----------------------------
# HELPERS
# -----------------------------
def load_txt(file_bytes: bytes) -> str:
    return file_bytes.decode("utf-8")


def load_pdf(file: UploadFile) -> str:
    reader = PdfReader(file.file)
    return "\n".join(page.extract_text() for page in reader.pages if page.extract_text())


def chunk_text(text: str, chunk_size=1000, overlap=200):
    chunks, start = [], 0
    while start < len(text):
        end = start + chunk_size
        chunks.append(text[start:end])
        start = end - overlap
    return chunks


def combine_chunks(matches):
    return "\n\n---\n\n".join([m["metadata"]["text"] for m in matches])


def ask_groq(query, context):
    prompt = f"""
You are a helpful legal assistant.
Use ONLY the given context to answer the question.
If not found, reply: "Not enough information."

Question: {query}

Context:
{context}

Answer:
"""
    response = groq_client.chat.completions.create(
        model="groq/compound-mini",
        messages=[{"role": "user", "content": prompt}],
        temperature=0.2
    )
    return response.choices[0].message.content

# -----------------------------
# ROUTES
# -----------------------------

@app.post("/upload")
async def upload_files(files: List[UploadFile] = File(...)):
    """Accept single or multiple files"""
    results = []

    for file in files:
        try:
            ext = os.path.splitext(file.filename)[1].lower()
            if ext == ".pdf":
                text = load_pdf(file)
            elif ext == ".txt":
                text = load_txt(await file.read())
            else:
                results.append({"filename": file.filename, "status": "error", "error": "Only .pdf or .txt allowed"})
                continue

            chunks = chunk_text(text)

            vectors = []
            for i, chunk in enumerate(chunks):
                emb = model.encode(chunk).tolist()
                vectors.append({
                    "id": str(uuid.uuid4()),
                    "values": emb,
                    "metadata": {
                        "text": chunk,
                        "source": file.filename,
                        "chunk": i
                    }
                })

            index.upsert(vectors=vectors)
            results.append({"filename": file.filename, "status": "success", "chunks": len(chunks)})

        except Exception as e:
            results.append({"filename": file.filename, "status": "error", "error": str(e)})

    return {"results": results}

@app.get("/ask")
def ask(query: str):
    try:
        query_embed = model.encode(query).tolist()
        results = index.query(
            vector=query_embed,
            top_k=5,
            include_metadata=True
        )

        context = combine_chunks(results["matches"])
        answer = ask_groq(query, context)

        return {
            "query": query,
            "answer": answer,
            "sources": [
                {
                    "id": m["id"],
                    "source": m["metadata"]["source"],
                    "chunk": m["metadata"]["chunk"],
                    "score": m["score"],
                }
                for m in results["matches"]
            ]
        }

    except Exception as e:
        return JSONResponse(status_code=500, content={"error": str(e)})

@app.get("/health")
def health():
    return {"status": "ok", "pinecone_index": index_name}

from typing import Any, List
import shutil
from pathlib import Path

from fastapi import FastAPI, HTTPException, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from backend.config import settings
from backend.ingest import ingest
from backend.rag import generate_answer, search, summarize_document, generate_quiz

app = FastAPI(title="Smart Campus Assistant API", version="0.1.0")

# Add CORS middleware to allow frontend to call backend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, replace with specific origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


class QueryRequest(BaseModel):
    question: str
    top_k: int | None = None


class QueryResponse(BaseModel):
    answer: str
    sources: List[dict[str, Any]]


class SummarizeRequest(BaseModel):
    query: str | None = None  # Optional query to focus summary
    max_length: int = 500


class SummarizeResponse(BaseModel):
    summary: str
    sources: List[dict[str, Any]]


class QuizRequest(BaseModel):
    query: str | None = None  # Optional query to focus quiz
    num_questions: int = 5
    difficulty: str = "medium"


class QuizResponse(BaseModel):
    quiz: dict
    sources: List[dict[str, Any]]


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok"}


# Debug endpoint removed - not exposed to users


@app.post("/ingest")
def ingest_docs() -> dict[str, str]:
    try:
        ingest()
        return {"status": "ingested", "message": "Documents successfully ingested"}
    except FileNotFoundError as exc:
        raise HTTPException(status_code=404, detail=str(exc))
    except RuntimeError as exc:
        raise HTTPException(status_code=400, detail=str(exc))
    except Exception as exc:
        raise HTTPException(status_code=500, detail=f"Error during ingestion: {str(exc)}")


@app.post("/query", response_model=QueryResponse)
def query(req: QueryRequest) -> QueryResponse:
    if not req.question or not req.question.strip():
        raise HTTPException(status_code=400, detail="Question cannot be empty")
    
    try:
        contexts = search(req.question.strip(), req.top_k or settings.top_k)
    except FileNotFoundError as exc:
        raise HTTPException(status_code=400, detail=str(exc))
    except ValueError as exc:
        raise HTTPException(status_code=500, detail=f"Search error: {str(exc)}")
    except Exception as exc:
        raise HTTPException(status_code=500, detail=f"Search failed: {str(exc)}")

    if not contexts:
        raise HTTPException(status_code=404, detail="No context found. Ingest documents first.")

    try:
        answer = generate_answer(req.question.strip(), contexts)
    except ValueError as exc:
        raise HTTPException(status_code=500, detail=f"Answer generation error: {str(exc)}")
    except Exception as exc:
        error_msg = str(exc)
        # Don't expose full traceback to frontend, but log it
        import logging
        logging.error(f"Error generating answer: {error_msg}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Error generating answer: {error_msg}")

    return QueryResponse(answer=answer, sources=contexts)


@app.post("/upload")
async def upload_file(file: UploadFile = File(...)) -> dict[str, str]:
    """Upload a file to the data directory"""
    allowed_extensions = {".pdf", ".txt", ".md", ".docx", ".doc", ".pptx", ".ppt"}
    file_ext = Path(file.filename).suffix.lower()
    
    if file_ext not in allowed_extensions:
        raise HTTPException(
            status_code=400,
            detail=f"File type {file_ext} not supported. Allowed: {', '.join(allowed_extensions)}"
        )
    
    try:
        data_dir = Path(settings.data_dir)
        data_dir.mkdir(parents=True, exist_ok=True)
        
        file_path = data_dir / file.filename
        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
        
        return {
            "status": "uploaded",
            "filename": file.filename,
            "message": f"File {file.filename} uploaded successfully"
        }
    except Exception as exc:
        raise HTTPException(status_code=500, detail=f"Error uploading file: {str(exc)}")


@app.post("/summarize", response_model=SummarizeResponse)
def summarize(req: SummarizeRequest) -> SummarizeResponse:
    """Summarize documents based on query or all documents"""
    try:
        if req.query:
            contexts = search(req.query.strip(), top_k=10)
        else:
            # Get top contexts from all documents
            contexts = search("summary overview main points", top_k=10)
    except FileNotFoundError as exc:
        raise HTTPException(status_code=400, detail=str(exc))
    except ValueError as exc:
        raise HTTPException(status_code=500, detail=f"Search error: {str(exc)}")
    except Exception as exc:
        raise HTTPException(status_code=500, detail=f"Search failed: {str(exc)}")

    if not contexts:
        raise HTTPException(status_code=404, detail="No context found. Ingest documents first.")

    try:
        summary = summarize_document(contexts, max_length=req.max_length)
    except ValueError as exc:
        raise HTTPException(status_code=500, detail=f"Summarization error: {str(exc)}")
    except Exception as exc:
        raise HTTPException(status_code=500, detail=f"Error generating summary: {str(exc)}")

    return SummarizeResponse(summary=summary, sources=contexts)


@app.post("/quiz", response_model=QuizResponse)
def create_quiz(req: QuizRequest) -> QuizResponse:
    """Generate a quiz based on query or all documents"""
    if req.num_questions < 1 or req.num_questions > 20:
        raise HTTPException(status_code=400, detail="Number of questions must be between 1 and 20")
    
    if req.difficulty not in ["easy", "medium", "hard"]:
        raise HTTPException(status_code=400, detail="Difficulty must be: easy, medium, or hard")
    
    try:
        if req.query and req.query.strip():
            # Use the specific topic query for better relevance
            query_text = req.query.strip()
            # Search with the topic query to get relevant contexts
            contexts = search(query_text, top_k=20)  # Get more contexts for better quiz generation
            # If not enough relevant contexts, supplement with general search
            if len(contexts) < 5:
                general_contexts = search("important concepts key points main ideas", top_k=10)
                # Merge and deduplicate
                seen_texts = {c["text"][:100] for c in contexts}
                for ctx in general_contexts:
                    if ctx["text"][:100] not in seen_texts:
                        contexts.append(ctx)
                        seen_texts.add(ctx["text"][:100])
        else:
            # Get top contexts from all documents
            contexts = search("important concepts key points main ideas", top_k=20)
    except FileNotFoundError as exc:
        raise HTTPException(status_code=400, detail=str(exc))
    except ValueError as exc:
        raise HTTPException(status_code=500, detail=f"Search error: {str(exc)}")
    except Exception as exc:
        raise HTTPException(status_code=500, detail=f"Search failed: {str(exc)}")

    if not contexts:
        raise HTTPException(status_code=404, detail="No context found. Ingest documents first.")

    try:
        topic = req.query.strip() if req.query and req.query.strip() else None
        quiz = generate_quiz(contexts, num_questions=req.num_questions, difficulty=req.difficulty, topic=topic)
    except ValueError as exc:
        raise HTTPException(status_code=500, detail=f"Quiz generation error: {str(exc)}")
    except Exception as exc:
        raise HTTPException(status_code=500, detail=f"Error generating quiz: {str(exc)}")

    return QuizResponse(quiz=quiz, sources=contexts)



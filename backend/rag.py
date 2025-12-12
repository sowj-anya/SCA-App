import json
import os
from pathlib import Path
from typing import List, Tuple

import faiss
import numpy as np
from groq import Groq
from sentence_transformers import SentenceTransformer

from backend.config import settings


# -----------------------------
# EMBEDDING HANDLER
# -----------------------------
class Embedder:
    _model: SentenceTransformer | None = None
    _groq_client: Groq | None = None

    @classmethod
    def get_groq_client(cls) -> Groq:
        if cls._groq_client is None:
            if not settings.groq_api_key:
                raise ValueError("GROQ_API_KEY is not set. Please set it in your .env file.")
            cls._groq_client = Groq(api_key=settings.groq_api_key)
        return cls._groq_client

    @classmethod
    def use_groq(cls):
        # Groq embeddings API may not be available, so use local embeddings by default
        return False  # Disable Groq embeddings, use local model instead

    @classmethod
    def get_model(cls):
        if cls._model is None:
            model_name = settings.embedding_model
            # Ensure we're using a valid sentence-transformers model
            # Remove any incorrect prefixes if present
            if model_name.startswith("sentence-transformers/"):
                model_name = model_name.replace("sentence-transformers/", "")
            # If it's still an invalid name, use the default
            if "nomic-embed-text" in model_name.lower() or model_name == "nomic-embed-text":
                model_name = "all-MiniLM-L6-v2"
                print(f"Warning: Invalid embedding model detected. Using default: {model_name}")
            cls._model = SentenceTransformer(model_name)
        return cls._model

    @classmethod
    def encode(cls, texts: List[str]) -> np.ndarray:
        if not texts or not any(t.strip() for t in texts):
            raise ValueError("Cannot encode empty texts")
        
        if cls.use_groq():
            try:
                client = cls.get_groq_client()
                resp = client.embeddings.create(
                    model="nomic-embed-text-v1",
                    input=texts
                )
                if not resp.data:
                    raise ValueError("No embeddings returned from Groq API")
                vectors = [item.embedding for item in resp.data]
                embeddings = np.array(vectors, dtype="float32")
                # Normalize embeddings for IndexFlatIP (inner product)
                norms = np.linalg.norm(embeddings, axis=1, keepdims=True)
                norms = np.where(norms == 0, 1, norms)  # Avoid division by zero
                embeddings = embeddings / norms
                return embeddings
            except Exception as e:
                raise ValueError(f"Groq embedding API error: {str(e)}")

        # Local model
        try:
            model = cls.get_model()
            embeddings = model.encode(texts, convert_to_numpy=True, normalize_embeddings=True)
            return np.array(embeddings, dtype="float32")
        except Exception as e:
            raise ValueError(f"Local embedding model error: {str(e)}")

# -----------------------------
# FAISS INDEX HANDLING
# -----------------------------
def load_index() -> Tuple[faiss.Index, list]:
    if not Path(settings.index_file).exists() or not Path(settings.metadata_file).exists():
        raise FileNotFoundError("Index or metadata missing. Run ingestion first.")
    index = faiss.read_index(settings.index_file)
    with open(settings.metadata_file, "r", encoding="utf-8") as f:
        metadata = json.load(f)
    return index, metadata


def save_index(index: faiss.Index, metadata: list) -> None:
    Path(settings.embeddings_dir).mkdir(parents=True, exist_ok=True)
    faiss.write_index(index, settings.index_file)
    with open(settings.metadata_file, "w", encoding="utf-8") as f:
        json.dump(metadata, f, ensure_ascii=False, indent=2)


def build_index(chunks: List[dict]) -> None:
    texts = [c["text"] for c in chunks]
    embeddings = Embedder.encode(texts)
    dim = embeddings.shape[1]
    # IndexFlatIP works with normalized vectors (inner product = cosine similarity)
    index = faiss.IndexFlatIP(dim)
    # Ensure embeddings are normalized (Embedder.encode should handle this)
    index.add(embeddings.astype("float32"))
    save_index(index, chunks)


def search(query: str, top_k: int) -> List[dict]:
    if not query or not query.strip():
        raise ValueError("Query cannot be empty")
    
    try:
        index, metadata = load_index()
    except Exception as e:
        raise FileNotFoundError(f"Failed to load index: {str(e)}")
    
    try:
        query_vec = Embedder.encode([query])
    except Exception as e:
        raise ValueError(f"Failed to encode query: {str(e)}")
    
    if query_vec.shape[1] != index.d:
        raise ValueError(f"Embedding dimension mismatch: query={query_vec.shape[1]}, index={index.d}")
    
    try:
        scores, idxs = index.search(query_vec, min(top_k, index.ntotal))
    except Exception as e:
        raise ValueError(f"FAISS search failed: {str(e)}")

    results = []
    for score, idx in zip(scores[0], idxs[0]):
        if idx < 0 or idx >= len(metadata):
            continue
        item = metadata[idx].copy()
        item["score"] = float(score)
        results.append(item)

    return results


# -----------------------------
# PROMPT BUILDING
# -----------------------------
def build_prompt(question: str, contexts: List[dict]) -> str:
    context_block = "\n\n".join(
        f"[Source: {c.get('source','unknown')}] {c['text']}" for c in contexts
    )
    prompt = (
        "You are a helpful Smart Campus Assistant. Use only the context to answer. "
        "If the answer is not in the context, say you do not know.\n\n"
        f"Context:\n{context_block}\n\nQuestion: {question}\nAnswer:"
    )
    return prompt


# -----------------------------
# ANSWER GENERATION (GROQ)
# -----------------------------
def generate_answer(question: str, contexts: List[dict]) -> str:
    if not settings.groq_api_key:
        raise ValueError("GROQ_API_KEY is not set. Please set it in your .env file.")
    
    if not question or not question.strip():
        raise ValueError("Question cannot be empty")
    
    if not contexts:
        raise ValueError("Contexts cannot be empty")
    
    try:
        client = Groq(api_key=settings.groq_api_key)
    except Exception as e:
        raise ValueError(f"Failed to initialize Groq client: {str(e)}")

    prompt = build_prompt(question, contexts)

    try:
        response = client.chat.completions.create(
            model=settings.llm_model,   # "llama-3.1-8b-instant"
            messages=[
                {"role": "system", "content": "You are a concise Smart Campus Assistant."},
                {"role": "user", "content": prompt},
            ],
            temperature=0.2,
        )
    except Exception as e:
        raise ValueError(f"Groq API call failed: {str(e)}")

    if not response.choices or not response.choices[0].message.content:
        raise ValueError("Empty response from Groq API")

    return response.choices[0].message.content.strip()


# -----------------------------
# DOCUMENT SUMMARIZATION
# -----------------------------
def summarize_document(contexts: List[dict], max_length: int = 500) -> str:
    """Summarize a document or set of contexts"""
    if not settings.groq_api_key:
        raise ValueError("GROQ_API_KEY is not set. Please set it in your .env file.")
    
    if not contexts:
        raise ValueError("Contexts cannot be empty")
    
    # Combine all contexts
    full_text = "\n\n".join([c["text"] for c in contexts])
    
    prompt = (
        f"Please provide a comprehensive summary of the following document(s). "
        f"Focus on key points, main ideas, and important details. "
        f"Keep the summary concise but informative (approximately {max_length} words).\n\n"
        f"Document content:\n{full_text}\n\n"
        f"Summary:"
    )
    
    try:
        client = Groq(api_key=settings.groq_api_key)
        response = client.chat.completions.create(
            model=settings.llm_model,
            messages=[
                {"role": "system", "content": "You are an expert at summarizing educational content. Provide clear, concise summaries."},
                {"role": "user", "content": prompt},
            ],
            temperature=0.3,
            max_tokens=max_length * 2,  # Allow enough tokens
        )
    except Exception as e:
        raise ValueError(f"Groq API call failed: {str(e)}")

    if not response.choices or not response.choices[0].message.content:
        raise ValueError("Empty response from Groq API")

    return response.choices[0].message.content.strip()


# -----------------------------
# QUIZ GENERATION
# -----------------------------
def generate_quiz(contexts: List[dict], num_questions: int = 5, difficulty: str = "medium", topic: str = None) -> dict:
    """Generate a quiz from the given contexts"""
    if not settings.groq_api_key:
        raise ValueError("GROQ_API_KEY is not set. Please set it in your .env file.")
    
    if not contexts:
        raise ValueError("Contexts cannot be empty")
    
    # Combine all contexts
    full_text = "\n\n".join([c["text"] for c in contexts])
    
    # Build topic-specific prompt
    topic_instruction = ""
    if topic and topic.strip():
        topic_instruction = f"IMPORTANT: Focus ALL questions on the topic: '{topic}'. Every question must be directly related to this topic.\n\n"
    
    prompt = (
        f"You are an expert quiz creator. Generate exactly {num_questions} {difficulty} difficulty multiple-choice questions "
        f"based ONLY on the following content. {topic_instruction}"
        f"Make sure questions are relevant and test understanding of the material.\n\n"
        f"For each question, you MUST provide:\n"
        f"1. A clear, specific question text\n"
        f"2. Exactly four answer options labeled A, B, C, and D\n"
        f"3. The correct answer (must be A, B, C, or D)\n"
        f"4. A brief explanation of why the answer is correct\n\n"
        f"IMPORTANT: Format your response as valid JSON only, with this exact structure:\n"
        f'{{"questions": [{{"question": "Your question here", "options": {{"A": "Option A text", "B": "Option B text", "C": "Option C text", "D": "Option D text"}}, "correct": "A", "explanation": "Why this is correct"}}]}}\n\n'
        f"Content to create questions from:\n{full_text[:6000]}\n\n"
        f"Generate exactly {num_questions} questions as JSON:"
    )
    
    try:
        client = Groq(api_key=settings.groq_api_key)
        response = client.chat.completions.create(
            model=settings.llm_model,
            messages=[
                {"role": "system", "content": "You are an expert at creating educational quizzes. Generate clear, well-structured questions."},
                {"role": "user", "content": prompt},
            ],
            temperature=0.7,
        )
    except Exception as e:
        raise ValueError(f"Groq API call failed: {str(e)}")

    if not response.choices or not response.choices[0].message.content:
        raise ValueError("Empty response from Groq API")

    import json
    import re
    
    response_text = response.choices[0].message.content.strip()
    
    # Try to extract JSON from the response
    # Look for JSON object
    json_match = re.search(r'\{[\s\S]*\}', response_text)
    if json_match:
        try:
            quiz_data = json.loads(json_match.group())
            if "questions" in quiz_data:
                return quiz_data
        except json.JSONDecodeError as e:
            # Try to fix common JSON issues
            try:
                # Remove markdown code blocks if present
                cleaned = re.sub(r'```json\s*', '', response_text)
                cleaned = re.sub(r'```\s*', '', cleaned)
                quiz_data = json.loads(cleaned)
                if "questions" in quiz_data:
                    return quiz_data
            except:
                pass
    
    # Fallback: Try to parse questions from text format
    questions = []
    question_pattern = r'(?:Question\s*\d+[:.]?\s*|Q\d+[:.]?\s*|^\d+[.)]\s*)(.+?)(?=\n(?:Question|Q\d+|\d+[.)]|$))'
    matches = re.finditer(question_pattern, response_text, re.MULTILINE | re.IGNORECASE | re.DOTALL)
    
    for match in list(matches)[:num_questions]:
        question_text = match.group(1).strip()
        # Try to extract options
        options_match = re.search(r'([A-D])[:.)]\s*(.+?)(?=\n[A-D][:.)]|$)', question_text, re.MULTILINE)
        if options_match:
            questions.append({
                "question": question_text.split('\n')[0],
                "options": {"A": "Option A", "B": "Option B", "C": "Option C", "D": "Option D"},
                "correct": "A",
                "explanation": "See source material for details."
            })
    
    if questions:
        return {"questions": questions}
    
    # Final fallback: return a single question with the response text
    return {
        "questions": [{
            "question": "Quiz generated from your documents. Please review the content below.",
            "options": {
                "A": "Review the source materials",
                "B": "Check the uploaded documents",
                "C": "Refer to course notes",
                "D": "Consult with instructor"
            },
            "correct": "A",
            "explanation": response_text[:500] + ("..." if len(response_text) > 500 else "")
        }]
    }

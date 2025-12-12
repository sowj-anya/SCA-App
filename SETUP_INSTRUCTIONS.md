# 🎓 SKCET Smart Campus Assistant - Setup Instructions

## Project Overview

**Smart Campus Assistant** is an AI-powered study companion designed for students at Sri Krishna College of Engineering and Technology (SKCET). It helps students efficiently learn from their course materials through:

- 📁 **Document Upload**: Drag-and-drop support for PDFs, Word docs, PowerPoints, and text files
- 💬 **Q&A Chat**: Ask questions and get accurate answers from uploaded materials
- 📝 **Document Summarization**: Automatically summarize long lecture notes and documents
- 🧪 **Quiz Generation**: Generate practice quizzes to test knowledge retention

## Technology Stack

- **Backend**: FastAPI (Python)
- **Frontend**: Streamlit (Python)
- **AI/LLM**: Groq API (Llama 3.1 8B Instant)
- **Embeddings**: Sentence Transformers (all-MiniLM-L6-v2)
- **Vector Store**: FAISS (Facebook AI Similarity Search)
- **RAG Architecture**: Retrieval-Augmented Generation

## Prerequisites

- Python 3.10 or higher
- Groq API Key (Get free API key at: https://console.groq.com/)
- Internet connection (for Groq API and model downloads)

## Installation Steps

### Step 1: Clone/Download the Project

```bash
# If using git
git clone <repository-url>
cd smartclgassisstant

# Or extract the project folder
```

### Step 2: Create Virtual Environment (Recommended)

**Windows:**
```bash
python -m venv .venv
.venv\Scripts\activate
```

**Linux/Mac:**
```bash
python3 -m venv .venv
source .venv/bin/activate
```

### Step 3: Install Dependencies

```bash
pip install -r requirements.txt
```

This will install:
- FastAPI and Uvicorn (backend server)
- Streamlit (frontend)
- FAISS (vector search)
- Sentence Transformers (embeddings)
- Groq (LLM API)
- And other required packages

### Step 4: Configure Environment Variables

1. Copy the environment template:
   ```bash
   copy env.example .env
   ```
   (Linux/Mac: `cp env.example .env`)

2. Edit `.env` file and add your Groq API key:
   ```
   GROQ_API_KEY=your_actual_groq_api_key_here
   ```

   **To get a Groq API key:**
   - Visit: https://console.groq.com/
   - Sign up for a free account
   - Create an API key
   - Copy and paste it into your `.env` file

### Step 5: Verify Installation

Check that all dependencies are installed:
```bash
python -c "import fastapi, uvicorn, streamlit, faiss, sentence_transformers, groq"
```

If no errors appear, installation is successful!

## Running the Application

### Option 1: Using Batch Files (Windows)

1. **Start Backend Server:**
   - Double-click `start_backend.bat`
   - OR run in terminal: `start_backend.bat`
   - Wait until you see: `Uvicorn running on http://0.0.0.0:8000`
   - **Keep this window open!**

2. **Start Frontend (in a NEW terminal):**
   - Double-click `start_frontend.bat`
   - OR run in terminal: `start_frontend.bat`
   - Browser will open automatically at `http://localhost:8501`

### Option 2: Manual Start

1. **Start Backend:**
   ```bash
   uvicorn backend.api:app --reload --host 0.0.0.0 --port 8000
   ```

2. **Start Frontend (in a NEW terminal):**
   ```bash
   streamlit run frontend/app.py
   ```

### Option 3: Using Python Scripts

1. **Start Backend:**
   ```bash
   python -m uvicorn backend.api:app --reload --host 0.0.0.0 --port 8000
   ```

2. **Start Frontend:**
   ```bash
   python -m streamlit run frontend/app.py
   ```

## First-Time Setup

1. **Upload Documents:**
   - Open the frontend in your browser
   - Go to "Upload Documents" tab
   - Drag and drop your course materials (PDFs, PPTs, Word docs)
   - Click "Upload" for each file
   - Documents will be processed automatically

2. **Verify Documents:**
   - Check "Your Documents" section to see uploaded files
   - Click "Process Documents" in sidebar if needed

3. **Start Using:**
   - Go to "Ask Questions" tab to ask questions
   - Use "Summarize" tab for document summaries
   - Use "Generate Quiz" tab for practice quizzes

## Troubleshooting

### ❌ "System is offline" Error

**Problem:** Backend server is not running.

**Solution:**
1. Make sure backend is running (check terminal for `Uvicorn running on http://0.0.0.0:8000`)
2. Visit http://localhost:8000/health in browser
3. Should show: `{"status":"ok"}`
4. If not, restart backend server

### ❌ "GROQ_API_KEY is not set" Error

**Problem:** API key not configured.

**Solution:**
1. Check that `.env` file exists
2. Verify `GROQ_API_KEY=your_key_here` is in `.env`
3. Restart backend server after adding key

### ❌ Port Already in Use

**Problem:** Port 8000 or 8501 is already in use.

**Solution:**
1. Close other applications using these ports
2. OR change ports in `.env`:
   ```
   BACKEND_PORT=8001
   ```
3. Update frontend `.env`:
   ```
   BACKEND_URL=http://localhost:8001
   ```

### ❌ "No documents found" Error

**Problem:** No documents uploaded or indexed.

**Solution:**
1. Upload documents in "Upload Documents" tab
2. Click "Process Documents" in sidebar
3. Wait for processing to complete

### ❌ Dependencies Not Found

**Problem:** Packages not installed.

**Solution:**
```bash
pip install -r requirements.txt
```

### ❌ Embedding Model Download Issues

**Problem:** First run downloads embedding model (~80MB).

**Solution:**
- Ensure internet connection
- Wait for download to complete
- Model is cached for future use

## Project Structure

```
smartclgassisstant/
├── backend/              # Backend API
│   ├── api.py           # FastAPI endpoints
│   ├── rag.py           # RAG functions (search, summarize, quiz)
│   ├── ingest.py         # Document processing
│   └── config.py         # Configuration
├── frontend/             # Frontend UI
│   └── app.py           # Streamlit application
├── data/                 # Uploaded documents (created automatically)
├── embeddings/           # FAISS index and metadata (created automatically)
├── requirements.txt      # Python dependencies
├── env.example           # Environment template
├── .env                  # Your configuration (create from env.example)
├── start_backend.bat     # Windows backend starter
├── start_frontend.bat    # Windows frontend starter
└── SETUP_INSTRUCTIONS.md # This file
```

## API Endpoints

- `GET /health` - Health check
- `POST /upload` - Upload a file
- `POST /ingest` - Process all documents
- `POST /query` - Ask a question
- `POST /summarize` - Generate summary
- `POST /quiz` - Generate quiz

## Features Explained

### 1. Document Upload
- Supports: PDF, DOCX, PPTX, TXT, MD
- Automatic text extraction
- Chunking for efficient search

### 2. Q&A Chat
- Natural language questions
- Answers sourced from uploaded documents
- Source citations provided

### 3. Document Summarization
- Focused or general summaries
- Adjustable length (200-1000 words)
- Key points extraction

### 4. Quiz Generation
- Multiple choice questions
- Three difficulty levels
- Explanations provided
- 3-15 questions per quiz

## RAG Architecture

1. **Document Ingestion:**
   - Documents are split into chunks
   - Each chunk is embedded using sentence transformers
   - Embeddings stored in FAISS vector index

2. **Query Processing:**
   - User question is embedded
   - Similar chunks retrieved from FAISS
   - Context sent to Groq LLM for answer generation

3. **Answer Generation:**
   - LLM uses retrieved context
   - Generates accurate, source-based answers
   - Returns answer with source citations

## Performance Tips

- **First Run:** May take time to download embedding model (~80MB)
- **Document Processing:** Large documents may take 30-60 seconds
- **Query Response:** Typically 2-5 seconds
- **Quiz Generation:** May take 10-20 seconds for 5 questions

## Support

For issues or questions:
- Check troubleshooting section above
- Verify all prerequisites are met
- Ensure `.env` file is configured correctly
- Check backend and frontend are both running

## License

This project is developed for SKCET Smart India Hackathon 2025.

---

**Developed for:** Sri Krishna College of Engineering and Technology  
**Website:** https://skcet.ac.in/  
**Project Theme:** Smart Campus Assistant


# 🎓 SKCET Smart Campus Assistant

**An AI-powered study companion for efficient learning**

[![SKCET](https://img.shields.io/badge/SKCET-Official-blue)](https://skcet.ac.in/)
[![Python](https://img.shields.io/badge/Python-3.10+-green)](https://www.python.org/)
[![FastAPI](https://img.shields.io/badge/FastAPI-Latest-teal)](https://fastapi.tiangolo.com/)
[![Streamlit](https://img.shields.io/badge/Streamlit-Latest-red)](https://streamlit.io/)

## 📋 Project Overview

**Smart Campus Assistant** is an intelligent AI-powered application designed for students at **Sri Krishna College of Engineering and Technology (SKCET)**. It helps students efficiently study from scattered lecture PDFs, notes, and course materials.

### 🎯 Key Features

- 📁 **Document Upload** - Drag-and-drop support for PDFs, Word documents, PowerPoints, and text files
- 💬 **Natural Language Q&A** - Ask questions and get accurate answers sourced from uploaded materials
- 📝 **Document Summarization** - Automatically summarize long lecture notes and documents
- 🧪 **Practice Quiz Generation** - Generate quizzes to test knowledge retention

## 🏫 About SKCET

**Sri Krishna College of Engineering and Technology** is a premier technical institution in South India, established in 1998. Located in Coimbatore, Tamil Nadu, SKCET offers 11 UG programmes, 4 PG programmes, and 8 research programmes.

- **Website:** https://skcet.ac.in/
- **Location:** Kuniamuthur, Coimbatore, Tamil Nadu - 641008
- **Established:** 1998
- **Accreditation:** 7 programmes accredited by NBA

## 🚀 Quick Start

### Prerequisites

- Python 3.10 or higher
- Groq API Key ([Get free key here](https://console.groq.com/))
- Internet connection

### Installation

1. **Clone/Download the project**
   ```bash
   cd smartclgassisstant
   ```

2. **Create virtual environment**
   ```bash
   python -m venv .venv
   .venv\Scripts\activate  # Windows
   # source .venv/bin/activate  # Linux/Mac
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Configure environment**
   ```bash
   copy env.example .env  # Windows
   # cp env.example .env  # Linux/Mac
   ```
   
   Edit `.env` and add your Groq API key:
   ```
   GROQ_API_KEY=your_actual_groq_api_key_here
   ```

5. **Start the application**
   
   **Backend (Terminal 1):**
   ```bash
   uvicorn backend.api:app --reload --host 0.0.0.0 --port 8000
   ```
   
   **Frontend (Terminal 2):**
   ```bash
   streamlit run frontend/app.py
   ```

6. **Open browser**
   - Frontend: http://localhost:8501
   - Backend API: http://localhost:8000

## 📖 Detailed Setup

For comprehensive setup instructions, troubleshooting, and feature explanations, see **[SETUP_INSTRUCTIONS.md](SETUP_INSTRUCTIONS.md)**

## 🛠️ Technology Stack

- **Backend:** FastAPI (Python)
- **Frontend:** Streamlit (Python)
- **AI/LLM:** Groq API (Llama 3.1 8B Instant)
- **Embeddings:** Sentence Transformers (all-MiniLM-L6-v2)
- **Vector Store:** FAISS (Facebook AI Similarity Search)
- **Architecture:** RAG (Retrieval-Augmented Generation)

## 📁 Project Structure

```
smartclgassisstant/
├── backend/              # FastAPI backend
│   ├── api.py           # API endpoints
│   ├── rag.py           # RAG functions
│   ├── ingest.py        # Document processing
│   └── config.py        # Configuration
├── frontend/            # Streamlit frontend
│   └── app.py           # Main UI
├── data/                # Uploaded documents
├── embeddings/          # FAISS index
├── requirements.txt     # Dependencies
└── SETUP_INSTRUCTIONS.md # Detailed guide
```

## 🎓 How to Use

1. **Upload Documents**
   - Go to "Upload Documents" tab
   - Drag and drop your course materials
   - Click "Upload" for each file
   - Documents are processed automatically

2. **Ask Questions**
   - Go to "Ask Questions" tab
   - Type your question
   - Get instant answers with source citations

3. **Summarize Documents**
   - Go to "Summarize" tab
   - Optionally specify a focus area
   - Generate concise summaries

4. **Practice Quizzes**
   - Go to "Generate Quiz" tab
   - Select topic, difficulty, and number of questions
   - Test your knowledge with AI-generated quizzes

## 🔧 API Endpoints

- `GET /health` - Health check
- `POST /upload` - Upload a file
- `POST /ingest` - Process documents
- `POST /query` - Ask a question
- `POST /summarize` - Generate summary
- `POST /quiz` - Generate quiz

## 🏆 Evaluation Criteria

This project addresses the Smart India Hackathon 2025 requirements:

✅ **Working Application** - Fully functional with all features  
✅ **AI/RAG Concepts** - Implements Retrieval-Augmented Generation  
✅ **Setup Instructions** - Comprehensive documentation provided  
✅ **User-Friendly Interface** - Clean, professional UI  
✅ **Multiple Data Sources** - Supports various document formats

## 📝 Features Explained

### RAG Architecture

1. **Document Ingestion:**
   - Documents split into semantic chunks
   - Embedded using sentence transformers
   - Stored in FAISS vector index

2. **Query Processing:**
   - User question embedded
   - Similar chunks retrieved
   - Context sent to LLM for answer generation

3. **Answer Generation:**
   - LLM uses retrieved context
   - Generates accurate, source-based answers
   - Returns with source citations

## 🐛 Troubleshooting

See **[SETUP_INSTRUCTIONS.md](SETUP_INSTRUCTIONS.md)** for detailed troubleshooting guide.

Common issues:
- **System offline:** Start backend server first
- **API key error:** Check `.env` file configuration
- **Port in use:** Change ports in `.env`
- **No documents:** Upload and process documents first

## 📞 Support

- **College Website:** https://skcet.ac.in/
- **Email:** principal@skcet.ac.in
- **Location:** Kuniamuthur, Coimbatore, Tamil Nadu - 641008

## 📄 License

Developed for SKCET Smart India Hackathon 2025.

## 🙏 Acknowledgments

- **Sri Krishna College of Engineering and Technology**
- **Smart India Hackathon 2025**
- **Groq** for LLM API
- **Open Source Community** for libraries and tools

---

**Developed with ❤️ for SKCET Students**

*Technology Education for a Better Future*

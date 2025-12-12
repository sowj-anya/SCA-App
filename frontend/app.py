import os
import requests
import streamlit as st
from pathlib import Path

BACKEND_URL = os.getenv("BACKEND_URL", "http://localhost:8000")

# Page configuration
st.set_page_config(
    page_title="SKCET Smart Campus Assistant",
    page_icon="🎓",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS with SKCET branding
st.markdown("""
    <style>
    .main-header {
        font-size: 2.8rem;
        font-weight: 700;
        color: #1a237e;
        margin-bottom: 0.5rem;
        text-align: center;
    }
    .sub-header {
        font-size: 1.2rem;
        color: #424242;
        margin-bottom: 2rem;
        text-align: center;
    }
    .skcet-brand {
        color: #1a237e;
        font-weight: 600;
    }
    .stButton>button {
        width: 100%;
        border-radius: 8px;
        background-color: #1a237e;
        color: white;
        font-weight: 600;
        padding: 0.5rem 1rem;
    }
    .stButton>button:hover {
        background-color: #283593;
    }
    .chat-message {
        padding: 1rem;
        border-radius: 8px;
        margin: 0.5rem 0;
    }
    .user-message {
        background-color: #e3f2fd;
        margin-left: 20%;
        padding: 1rem;
        border-radius: 8px;
    }
    .assistant-message {
        background-color: #f5f5f5;
        margin-right: 20%;
        padding: 1rem;
        border-radius: 8px;
    }
    .quiz-question {
        padding: 1rem;
        background-color: #fff;
        border-left: 4px solid #1a237e;
        margin: 1rem 0;
        border-radius: 4px;
    }
    .file-card {
        padding: 1rem;
        background-color: #f8f9fa;
        border-radius: 8px;
        margin: 0.5rem 0;
        border: 1px solid #e0e0e0;
    }
    .info-box {
        padding: 1rem;
        background-color: #e8eaf6;
        border-left: 4px solid #1a237e;
        border-radius: 4px;
        margin: 1rem 0;
    }
    </style>
""", unsafe_allow_html=True)

# Initialize session state
if "chat_history" not in st.session_state:
    st.session_state.chat_history = []
if "uploaded_files" not in st.session_state:
    st.session_state.uploaded_files = []
if "current_quiz" not in st.session_state:
    st.session_state.current_quiz = None
if "quiz_answers" not in st.session_state:
    st.session_state.quiz_answers = {}
if "quiz_checked" not in st.session_state:
    st.session_state.quiz_checked = {}


def format_file_size(size_bytes):
    """Format file size in human-readable format"""
    if size_bytes < 1024:
        return f"{size_bytes} B"
    elif size_bytes < 1024 * 1024:
        return f"{size_bytes / 1024:.1f} KB"
    else:
        return f"{size_bytes / (1024 * 1024):.1f} MB"


def call_query_api(question: str, top_k: int = 4):
    """Call the query API"""
    try:
        resp = requests.post(
            f"{BACKEND_URL}/query",
            json={"question": question, "top_k": top_k},
            timeout=60
        )
        resp.raise_for_status()
        return resp.json()
    except requests.exceptions.ConnectionError:
        raise RuntimeError("Unable to connect to the server. Please make sure the application is running.")
    except requests.exceptions.Timeout:
        raise RuntimeError("Request took too long. Please try again.")
    except requests.exceptions.HTTPError:
        try:
            error_data = resp.json()
            detail = error_data.get("detail", "An error occurred")
            if "No context found" in detail or "Index or metadata missing" in detail:
                raise RuntimeError("No documents found. Please upload and process your documents first.")
            elif "GROQ_API_KEY" in detail:
                raise RuntimeError("Configuration error. Please contact support.")
            else:
                raise RuntimeError("Unable to process your question. Please try again.")
        except RuntimeError:
            raise
        except:
            raise RuntimeError("An error occurred. Please try again.")


def upload_file_to_backend(uploaded_file):
    """Upload file to backend"""
    try:
        files = {"file": (uploaded_file.name, uploaded_file.getvalue(), uploaded_file.type)}
        resp = requests.post(f"{BACKEND_URL}/upload", files=files, timeout=60)
        resp.raise_for_status()
        return resp.json()
    except requests.exceptions.HTTPError:
        try:
            error_data = resp.json()
            detail = error_data.get("detail", "Upload failed")
            if "not supported" in detail.lower():
                raise RuntimeError("This file type is not supported. Please upload PDF, Word, PowerPoint, or text files.")
            else:
                raise RuntimeError("Failed to upload file. Please try again.")
        except:
            raise RuntimeError("Failed to upload file. Please try again.")
    except Exception:
        raise RuntimeError("Failed to upload file. Please check your connection and try again.")


def call_summarize_api(query: str = None, max_length: int = 500):
    """Call the summarize API"""
    try:
        resp = requests.post(
            f"{BACKEND_URL}/summarize",
            json={"query": query, "max_length": max_length},
            timeout=60
        )
        resp.raise_for_status()
        return resp.json()
    except requests.exceptions.ConnectionError:
        raise RuntimeError("Unable to connect to the server. Please make sure the application is running.")
    except Exception:
        raise RuntimeError("Unable to generate summary. Please try again.")


def call_quiz_api(query: str = None, num_questions: int = 5, difficulty: str = "medium"):
    """Call the quiz API"""
    try:
        resp = requests.post(
            f"{BACKEND_URL}/quiz",
            json={"query": query, "num_questions": num_questions, "difficulty": difficulty},
            timeout=60
        )
        resp.raise_for_status()
        return resp.json()
    except requests.exceptions.ConnectionError:
        raise RuntimeError("Unable to connect to the server. Please make sure the application is running.")
    except Exception:
        raise RuntimeError("Unable to generate quiz. Please try again.")


def call_ingest_api():
    """Trigger document ingestion"""
    try:
        resp = requests.post(f"{BACKEND_URL}/ingest", timeout=120)
        resp.raise_for_status()
        return resp.json()
    except Exception:
        raise RuntimeError("Failed to process documents. Please try again.")


def check_backend_status():
    """Check if backend is available"""
    try:
        resp = requests.get(f"{BACKEND_URL}/health", timeout=5)
        return resp.status_code == 200
    except:
        return False


# Sidebar
with st.sidebar:
    st.markdown("## 🎓 SKCET")
    st.markdown("### Smart Campus Assistant")
    st.markdown("---")
    
    
    st.markdown("### Quick Actions")
    
    if st.button("🔄 Process Documents", use_container_width=True, help="Update the document index with all uploaded files"):
        if backend_online:
            with st.spinner("Processing..."):
                try:
                    result = call_ingest_api()
                    st.success("Documents processed successfully!")
                    st.balloons()
                except Exception as e:
                    st.error(str(e))
        else:
            st.error("System is offline. Please start the server first.")
    
    st.markdown("---")
    st.markdown("### 📖 How to Use")
    st.markdown("""
    1. **Upload** your course materials
    2. **Ask** questions about your documents
    3. **Summarize** long documents
    4. **Practice** with generated quizzes
    """)
    
    st.markdown("---")
    st.markdown("### 🏫 About SKCET")
    st.markdown("""
    **Sri Krishna College of Engineering and Technology**
    
    Established: 1998  
    Location: Coimbatore, Tamil Nadu
    
    [Visit Website](https://skcet.ac.in/)
    """)

     # Status check
    backend_online = check_backend_status()
    if backend_online:
        st.success("✅ System Ready")
    else:
        st.error("⚠️ System Offline")
        with st.expander("📋 How to Start the Server", expanded=True):
            st.markdown("""
            **To start the backend server:**
            
            1. Open a new terminal/command prompt
            2. Navigate to this project folder
            3. Run: `start_backend.bat` (Windows)
            4. Wait until you see: `Uvicorn running on http://0.0.0.0:8000`
            5. Keep that window open!
            6. Refresh this page
            
            **Quick Check:**
            - Visit http://localhost:8000/health
            - Should show: `{"status":"ok"}`
            """)
    
    st.markdown("---")


# Main header
st.markdown('<p class="main-header">🎓 SKCET Smart Campus Assistant</p>', unsafe_allow_html=True)
st.markdown('<p class="sub-header"> AI-powered study companion for efficient learning</p>', unsafe_allow_html=True)

# Info box
st.markdown("""
<div class="info-box">
    <strong>Welcome!</strong> Upload your course materials (PDFs, documents, PPTs) and get instant answers, 
    summaries, and practice quizzes powered by AI.
</div>
""", unsafe_allow_html=True)

# Tabs
tab1, tab2, tab3, tab4 = st.tabs(["📁 Upload Documents", "💬 Ask Questions", "📝 Summarize", "🧪 Generate Quiz"])

# Tab 1: File Upload
with tab1:
    st.header("Upload Course Materials")
    st.markdown("Upload your PDFs, documents, PowerPoints, or text files to get started.")
    
    col1, col2 = st.columns([2, 1])
    
    with col1:
        uploaded_files = st.file_uploader(
            "Drag and drop files here or click to browse",
            type=["pdf", "txt", "md", "docx", "doc", "pptx", "ppt"],
            accept_multiple_files=True,
            help="Supported formats: PDF, TXT, MD, DOCX, PPTX"
        )
    
    with col2:
        st.markdown("### 📋 Supported Formats")
        st.markdown("""
        - 📄 PDF Documents
        - 📝 Text Files (.txt, .md)
        - 📊 Word Documents (.docx, .doc)
        - 🎯 PowerPoint (.pptx, .ppt)
        """)
    
    if uploaded_files:
        st.markdown("### Ready to Upload")
        for uploaded_file in uploaded_files:
            with st.container():
                col1, col2, col3 = st.columns([3, 1, 1])
                with col1:
                    st.markdown(f'<div class="file-card">', unsafe_allow_html=True)
                    st.markdown(f"**{uploaded_file.name}**")
                    st.markdown(f"*{format_file_size(uploaded_file.size)}*")
                    st.markdown('</div>', unsafe_allow_html=True)
                with col2:
                    if st.button("📤 Upload", key=f"upload_{uploaded_file.name}", use_container_width=True):
                        if backend_online:
                            with st.spinner(f"Uploading {uploaded_file.name}..."):
                                try:
                                    result = upload_file_to_backend(uploaded_file)
                                    st.success("✅ Uploaded successfully!")
                                    # Auto-process after upload
                                    with st.spinner("Processing document..."):
                                        try:
                                            ingest_result = call_ingest_api()
                                            st.success("✅ Document processed and ready!")
                                            st.balloons()
                                        except Exception as e:
                                            st.warning("Uploaded but processing failed. Click 'Process Documents' in sidebar.")
                                except Exception as e:
                                    st.error(str(e))
                        else:
                            st.error("System offline")
                with col3:
                    if st.button("❌", key=f"remove_{uploaded_file.name}", use_container_width=True):
                        st.rerun()
    
    # Show existing files
    st.markdown("---")
    st.markdown("### 📚 Your Documents")
    data_dir = Path("data")
    if data_dir.exists():
        files = [f for f in data_dir.glob("*") if f.is_file() and not f.name.startswith(".")]
        if files:
            for file in files:
                st.markdown(f'<div class="file-card">📄 **{file.name}** *({format_file_size(file.stat().st_size)})*</div>', unsafe_allow_html=True)
        else:
            st.info("👆 Upload your first document above to get started!")
    else:
        st.info("👆 Upload files to begin")


# Tab 2: Q&A Chat
with tab2:
    st.header("Ask Questions")
    st.markdown("Ask questions about your course materials and get instant answers.")
    
    if not backend_online:
        st.warning("⚠️ System is offline. Please start the backend server first.")
        st.info("💡 Check the sidebar for instructions on how to start the server.")
    
    # Chat interface
    if st.session_state.chat_history:
        st.markdown("### Conversation History")
        for i, message in enumerate(st.session_state.chat_history):
            if message["role"] == "user":
                st.markdown(f'<div class="chat-message user-message"><strong>You:</strong> {message["content"]}</div>', unsafe_allow_html=True)
            else:
                st.markdown(f'<div class="chat-message assistant-message"><strong>Assistant:</strong> {message["content"]}</div>', unsafe_allow_html=True)
                if "sources" in message and message["sources"]:
                    with st.expander("📚 View Sources"):
                        for src in message["sources"][:3]:
                            st.markdown(f"**{src.get('source', 'Document')}**")
                            st.markdown(f"_{src.get('text', '')[:200]}..._")
        st.markdown("---")
    
    # Input area
    col1, col2 = st.columns([5, 1])
    
    with col1:
        user_question = st.text_input(
            "Ask a question about your documents",
            placeholder="e.g., What are the main topics covered?",
            label_visibility="collapsed"
        )
    
    with col2:
        ask_button = st.button("Ask ➤", use_container_width=True, type="primary")
    
    if ask_button and user_question.strip():
        if backend_online:
            with st.spinner("Thinking..."):
                try:
                    result = call_query_api(user_question.strip())
                    
                    # Add to chat history
                    st.session_state.chat_history.append({
                        "role": "user",
                        "content": user_question
                    })
                    st.session_state.chat_history.append({
                        "role": "assistant",
                        "content": result["answer"],
                        "sources": result["sources"]
                    })
                    
                    st.rerun()
                except Exception as e:
                    st.error(str(e))
        else:
            st.error("System is offline. Please start the server first.")


# Tab 3: Summarization
with tab3:
    st.header("Document Summarization")
    st.markdown("Generate concise summaries of your course materials.")
    
    if not backend_online:
        st.warning("⚠️ System is offline. Please start the backend server first.")
        st.info("💡 Check the sidebar for instructions on how to start the server.")
    
    col1, col2 = st.columns([2, 1])
    
    with col1:
        summary_query = st.text_input(
            "Focus area (optional)",
            placeholder="e.g., machine learning concepts, or leave empty for general summary",
            help="Enter a specific topic to focus the summary, or leave empty for a general summary"
        )
    
    with col2:
        max_length = st.slider("Summary Length", 20, 1000, 500, 50)
    
    if st.button("📝 Generate Summary", use_container_width=True, type="primary"):
        if backend_online:
            with st.spinner("Generating summary..."):
                try:
                    result = call_summarize_api(
                        query=summary_query if summary_query.strip() else None,
                        max_length=max_length
                    )
                    
                    st.markdown("### 📄 Summary")
                    st.markdown(result["summary"])
                    
                    st.markdown("---")
                    with st.expander("📚 Source Documents"):
                        for src in result["sources"][:5]:
                            st.markdown(f"**{src.get('source', 'Document')}**")
                            st.markdown(f"_{src.get('text', '')[:150]}..._")
                            st.markdown("---")
                except Exception as e:
                    st.error(str(e))
        else:
            st.error("System is offline. Please start the server first.")


# Tab 4: Quiz Generation
with tab4:
    st.header("Practice Quiz Generator")
    st.markdown("Test your knowledge with AI-generated quizzes from your materials.")
    
    if not backend_online:
        st.warning("⚠️ System is offline. Please start the backend server first.")
        st.info("💡 Check the sidebar for instructions on how to start the server.")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        quiz_query = st.text_input(
            "Topic (optional)",
            placeholder="e.g., data structures, or leave empty for general quiz",
            help="Enter a specific topic, or leave empty for a general quiz"
        )
    
    with col2:
        num_questions = st.slider("Number of Questions", 3, 15, 5, 1)
    
    with col3:
        difficulty = st.selectbox("Difficulty", ["Easy", "Medium", "Hard"], index=1)
    
    # Generate quiz button
    if st.button("🧪 Generate Quiz", use_container_width=True, type="primary", key="generate_quiz_btn"):
        if backend_online:
            with st.spinner("Generating quiz..."):
                try:
                    result = call_quiz_api(
                        query=quiz_query if quiz_query.strip() else None,
                        num_questions=num_questions,
                        difficulty=difficulty.lower()
                    )
                    
                    quiz = result.get("quiz", {})
                    questions = quiz.get("questions", [])
                    
                    if questions:
                        # Store quiz in session state
                        st.session_state.current_quiz = {
                            "questions": questions,
                            "topic": quiz_query if quiz_query.strip() else "General",
                            "difficulty": difficulty,
                            "sources": result.get("sources", [])
                        }
                        # Reset answers when new quiz is generated
                        st.session_state.quiz_answers = {}
                        st.session_state.quiz_checked = {}
                        st.rerun()
                    else:
                        st.warning("No questions generated. Please ensure you have uploaded documents.")
                except Exception as e:
                    st.error(str(e))
        else:
            st.error("System is offline. Please start the server first.")
    
    # Display quiz if it exists in session state
    if st.session_state.current_quiz and st.session_state.current_quiz.get("questions"):
        questions = st.session_state.current_quiz["questions"]
        topic = st.session_state.current_quiz.get("topic", "General")
        quiz_difficulty = st.session_state.current_quiz.get("difficulty", "Medium")
        
        st.markdown("### 🧪 Your Practice Quiz")
        st.markdown(f"**Topic:** {topic} | **Difficulty:** {quiz_difficulty.title()} | **Questions:** {len(questions)}")
        st.markdown("---")
        
        for i, q in enumerate(questions, 1):
            with st.container():
                st.markdown(f'<div class="quiz-question">', unsafe_allow_html=True)
                st.markdown(f"#### Question {i}")
                st.markdown(f"**{q.get('question', 'N/A')}**")
                
                options = q.get("options", {})
                if options:
                    # Initialize answer tracking
                    answer_key = f"quiz_answer_{i}"
                    check_key = f"quiz_check_{i}"
                    
                    if answer_key not in st.session_state.quiz_answers:
                        st.session_state.quiz_answers[answer_key] = None
                    if check_key not in st.session_state.quiz_checked:
                        st.session_state.quiz_checked[check_key] = False
                    
                    # Radio button for answer selection
                    current_answer = st.session_state.quiz_answers.get(answer_key)
                    default_index = None
                    if current_answer and current_answer in options:
                        default_index = list(options.keys()).index(current_answer)
                    
                    selected = st.radio(
                        "Select your answer:",
                        options=list(options.keys()),
                        format_func=lambda x: f"{x}: {options[x]}",
                        key=f"quiz_radio_{i}",
                        index=default_index
                    )
                    
                    # Update selected answer in session state immediately
                    if selected:
                        st.session_state.quiz_answers[answer_key] = selected
                    
                    # Check Answer button
                    col1, col2 = st.columns([1, 4])
                    with col1:
                        check_button = st.button(f"✓ Check Answer", key=check_key, use_container_width=True)
                    
                    # Handle button click and show result immediately
                    if check_button:
                        current_selected = st.session_state.quiz_answers.get(answer_key) or selected
                        if current_selected:
                            st.session_state.quiz_checked[check_key] = True
                            st.session_state.quiz_answers[answer_key] = current_selected
                            
                            # Show result immediately
                            correct = q.get("correct", "").upper().strip()
                            selected_upper = current_selected.upper().strip()
                            
                            if selected_upper == correct:
                                st.success(f"✅ **Correct!** {correct} is the right answer.")
                            else:
                                st.error(f"❌ **Incorrect.** The correct answer is **{correct}**.")
                            
                            explanation = q.get('explanation', 'No explanation provided.')
                            if explanation:
                                st.info(f"**Explanation:** {explanation}")
                        else:
                            st.warning("⚠️ Please select an answer first!")
                    elif st.session_state.quiz_checked.get(check_key, False):
                        # Show previous result if already checked (persists after rerun)
                        prev_answer = st.session_state.quiz_answers.get(answer_key)
                        if prev_answer:
                            correct = q.get("correct", "").upper().strip()
                            prev_upper = prev_answer.upper().strip()
                            
                            if prev_upper == correct:
                                st.success(f"✅ **Correct!** {correct} is the right answer.")
                            else:
                                st.error(f"❌ **Incorrect.** The correct answer is **{correct}**.")
                            
                            explanation = q.get('explanation', 'No explanation provided.')
                            if explanation:
                                st.info(f"**Explanation:** {explanation}")
                
                st.markdown('</div>', unsafe_allow_html=True)
                st.markdown("---")
        
        with st.expander("📚 Source Materials"):
            sources = st.session_state.current_quiz.get("sources", [])
            for src in sources[:3]:
                st.markdown(f"**{src.get('source', 'Document')}**")

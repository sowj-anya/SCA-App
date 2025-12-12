# 🚀 Quick Start - Backend Server

## Step-by-Step Instructions

### Step 1: Open Command Prompt/Terminal

Press `Windows Key + R`, type `cmd`, and press Enter.

### Step 2: Navigate to Project Folder

```bash
cd "C:\Users\sowjanya k\smartclgassisstant"
```

### Step 3: Check if .env file exists

```bash
dir .env
```

If it says "File Not Found", create it:
```bash
copy env.example .env
```

Then edit `.env` file and add your Groq API key:
```
GROQ_API_KEY=your_actual_groq_api_key_here
```

### Step 4: Activate Virtual Environment (if exists)

```bash
.venv\Scripts\activate
```

If you don't have a virtual environment, install dependencies globally:
```bash
pip install -r requirements.txt
```

### Step 5: Start Backend Server

**Option A: Using the batch file**
```bash
start_backend.bat
```

**Option B: Manual start**
```bash
uvicorn backend.api:app --reload --host 0.0.0.0 --port 8000
```

### Step 6: Verify Backend is Running

You should see:
```
INFO:     Uvicorn running on http://0.0.0.0:8000 (Press CTRL+C to quit)
INFO:     Started reloader process
INFO:     Started server process
INFO:     Waiting for application startup.
INFO:     Application startup complete.
```

### Step 7: Test Backend

Open a NEW browser tab and visit:
```
http://localhost:8000/health
```

You should see: `{"status":"ok"}`

### Step 8: Keep Terminal Open!

**IMPORTANT:** Keep the backend terminal window open. The server must keep running.

### Step 9: Start Frontend (in a NEW terminal)

Open another Command Prompt and run:
```bash
cd "C:\Users\sowjanya k\smartclgassisstant"
streamlit run frontend/app.py
```

## Common Errors and Solutions

### Error: "Module not found"
**Solution:** Install dependencies
```bash
pip install -r requirements.txt
```

### Error: "Port 8000 already in use"
**Solution:** Close other applications using port 8000, or change port:
```bash
uvicorn backend.api:app --reload --host 0.0.0.0 --port 8001
```

### Error: ".env file not found"
**Solution:** Create it:
```bash
copy env.example .env
```
Then edit `.env` and add your `GROQ_API_KEY`

### Error: "GROQ_API_KEY is not set"
**Solution:** Add your API key to `.env` file:
```
GROQ_API_KEY=gsk_your_actual_key_here
```

## Quick Test Commands

Test if backend is running:
```bash
curl http://localhost:8000/health
```

Or visit in browser: http://localhost:8000/health

## Still Having Issues?

Run the diagnostic script:
```bash
check_status.bat
```

This will check:
- Backend status
- Frontend status  
- Configuration
- Dependencies


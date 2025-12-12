# 🚀 Quick Start Guide

## Step 1: Install Dependencies

Open a terminal/command prompt and run:

```bash
pip install -r requirements.txt
```

## Step 2: Set Up Environment

1. Copy the environment template:
   ```bash
   copy env.example .env
   ```

2. Edit `.env` file and add your Groq API key:
   ```
   GROQ_API_KEY=your_actual_groq_api_key_here
   ```
   
   Get your free API key at: https://console.groq.com/

## Step 3: Start Backend Server

**Option A: Using the batch file (Windows)**
- Double-click `start_backend.bat`
- OR run: `start_backend.bat` in command prompt

**Option B: Manual start**
```bash
uvicorn backend.api:app --reload --host 0.0.0.0 --port 8000
```

You should see:
```
INFO:     Uvicorn running on http://0.0.0.0:8000
```

✅ **Keep this window open!** The backend must be running.

## Step 4: Start Frontend

Open a **NEW** terminal/command prompt window:

**Option A: Using the batch file (Windows)**
- Double-click `start_frontend.bat`
- OR run: `start_frontend.bat` in command prompt

**Option B: Manual start**
```bash
streamlit run frontend/app.py
```

The frontend will open automatically in your browser at `http://localhost:8501`

## Step 5: Upload Documents

1. Go to the **"Upload Documents"** tab
2. Drag and drop your PDFs, Word docs, or PowerPoint files
3. Click **"Upload"** for each file
4. Documents will be processed automatically

## Troubleshooting

### ❌ "System is offline" Error

**Solution:** The backend server is not running.

1. Make sure you completed Step 3 above
2. Check that the backend terminal shows: `Uvicorn running on http://0.0.0.0:8000`
3. Try accessing http://localhost:8000/health in your browser
   - Should show: `{"status":"ok"}`

### ❌ "GROQ_API_KEY is not set" Error

**Solution:** 
1. Make sure you created a `.env` file
2. Check that it contains: `GROQ_API_KEY=your_key_here`
3. Restart the backend server after adding the key

### ❌ Port Already in Use

**Solution:** Another application is using port 8000.

1. Close other applications using port 8000
2. OR change the port in `.env`: `BACKEND_PORT=8001`
3. Update frontend `.env`: `BACKEND_URL=http://localhost:8001`

### ❌ Dependencies Not Found

**Solution:**
```bash
pip install -r requirements.txt
```

## Need Help?

- Check that both backend and frontend are running
- Backend should be on port 8000
- Frontend should be on port 8501
- Make sure your `.env` file has the correct GROQ_API_KEY


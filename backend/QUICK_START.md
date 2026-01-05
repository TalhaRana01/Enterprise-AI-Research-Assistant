# Quick Start Guide - AI Research Assistant

## 🚀 Server Start Karna

### Option 1: Using Script (Recommended)
```powershell
.\scripts\start_server.ps1
```

### Option 2: Direct Command
```powershell
# Activate venv
.\venv\Scripts\activate

# Start server
uvicorn src.main:app --host 0.0.0.0 --port 8000 --reload
```

### Option 3: Python Direct
```powershell
python src/main.py
```

---

## ✅ Server Start Hone Ke Baad

### 1. Health Check
```powershell
# Browser mein:
http://localhost:8000/health

# Ya PowerShell:
Invoke-RestMethod -Uri http://localhost:8000/health
```

### 2. API Documentation
```
http://localhost:8000/docs
```

### 3. Test Endpoints
```powershell
# Search papers
Invoke-RestMethod -Uri "http://localhost:8000/api/v1/search?query=transformer+models&max_results=5"

# Or use test script
.\scripts\test_api.ps1
```

---

## 📋 Pre-requisites

### 1. Environment Variables
`.env` file mein ye zaroori hain:
```env
OPENAI_API_KEY=your-openai-key-here
SECRET_KEY=your-secret-key
VECTOR_DB_TYPE=chroma
```

### 2. Dependencies
```powershell
pip install -r requirements.txt
```

### 3. Vector Database
- **Development**: Chroma (automatic, no setup needed)
- **Production**: Pinecone (requires API key)

---

## 🧪 Testing

### Manual Test:
```powershell
# 1. Health check
curl http://localhost:8000/health

# 2. Search
curl http://localhost:8000/api/v1/search?query=AI

# 3. Chat
curl -X POST http://localhost:8000/api/v1/chat `
  -H "Content-Type: application/json" `
  -d '{\"question\": \"What is AI?\"}'
```

### Using Test Script:
```powershell
.\scripts\test_api.ps1
```

---

## 🐛 Common Issues

### Issue 1: Port Already in Use
```powershell
# Solution: Use different port
uvicorn src.main:app --port 8001
```

### Issue 2: OpenAI API Key Missing
```powershell
# Check .env file
Get-Content .env | Select-String "OPENAI"
```

### Issue 3: Import Errors
```powershell
# Reinstall dependencies
pip install -r requirements.txt --upgrade
```

---

## 📊 API Endpoints

### Search
- `GET /api/v1/search?query=...`
- `POST /api/v1/search`

### Chat/Q&A
- `POST /api/v1/chat`
- `POST /api/v1/chat/stream`

### Papers
- `POST /api/v1/papers/summarize`
- `GET /api/v1/papers/{paper_id}/summarize`
- `POST /api/v1/papers/cite`
- `GET /api/v1/papers/{paper_id}`

### Utility
- `GET /health`
- `GET /docs` (Swagger UI)

---

**Happy Coding! 🎉**


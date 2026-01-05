# Backend Structure - AI Research Assistant

## 📁 Complete Backend Directory Structure

```
backend/
├── src/                          # Source code
│   ├── main.py                  # FastAPI app entry point
│   ├── agents/                  # AI Agents
│   │   ├── router_agent.py
│   │   ├── search_agent.py
│   │   ├── qa_agent.py
│   │   └── summarization_agent.py
│   ├── chains/                  # LangChain Chains
│   │   ├── vector_store.py
│   │   ├── rag_chain.py
│   │   ├── citation_chain.py
│   │   └── summarization_chain.py
│   ├── tools/                   # Agent Tools
│   │   ├── arxiv_tool.py
│   │   ├── pdf_tool.py
│   │   └── search_tool.py
│   ├── loaders/                 # Document Loaders
│   │   ├── arxiv_loader.py
│   │   └── pdf_loader.py
│   ├── api/                     # API Layer
│   │   ├── routes/
│   │   │   ├── search.py
│   │   │   ├── chat.py
│   │   │   └── papers.py
│   │   └── models/
│   │       └── schemas.py
│   ├── config/                  # Configuration
│   │   └── settings.py
│   ├── prompts/                 # Prompt Templates
│   │   ├── prompt_manager.py
│   │   ├── system_prompt.txt
│   │   ├── search_prompt.txt
│   │   ├── qa_prompt.txt
│   │   ├── summarization_prompt.txt
│   │   └── citation_prompt.txt
│   └── utils/                   # Utilities
│       ├── logger.py
│       ├── validators.py
│       └── formatters.py
│
├── tests/                        # Test Suite
│   ├── unit/                    # Unit tests
│   ├── integration/             # Integration tests
│   └── e2e/                     # E2E tests
│
├── scripts/                      # Utility Scripts
│   ├── start_server.ps1
│   ├── test_api.ps1
│   ├── run_tests.ps1
│   └── setup_directories.ps1
│
├── data/                        # Local Data Storage
│   └── chroma/                  # Chroma vector DB
│
├── logs/                        # Application Logs
│
├── docs/                        # Documentation
│
├── requirements.txt             # Python Dependencies
├── pytest.ini                   # Pytest Configuration
├── docker-compose.yml           # Docker Compose (Backend Services)
├── coverage.xml                 # Test Coverage Report
│
├── README.md                    # Backend Documentation
├── QUICK_START.md               # Quick Start Guide
├── TESTING_GUIDE.md             # Testing Guide
├── PROJECT_STRUCTURE.md          # Project Structure
└── FRONTEND_COMPARISON.md        # Frontend Comparison (for reference)
```

## 🚀 Quick Commands

### Start Server
```powershell
cd backend
.\scripts\start_server.ps1
```

### Run Tests
```powershell
cd backend
pytest
```

### Install Dependencies
```powershell
cd backend
pip install -r requirements.txt
```

## 📝 Important Files

- **`src/main.py`** - FastAPI application entry point
- **`requirements.txt`** - All Python dependencies
- **`pytest.ini`** - Test configuration
- **`.env`** - Environment variables (create from `.env.example`)

## 🔗 Related Files

- **Root `README.md`** - Main project documentation
- **Root `docker-compose.yml`** - Full stack deployment (if exists)
- **`frontend/`** - Frontend application (separate)

---

**All backend files are now organized in the `backend/` folder! ✅**


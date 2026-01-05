# Project Structure - AI Research Assistant

## 📁 Complete Directory Structure

```
ai-research-assistant/
│
├── backend/                          # FastAPI Backend
│   ├── src/                          # Source code
│   │   ├── __init__.py
│   │   ├── main.py                   # FastAPI app entry point
│   │   │
│   │   ├── agents/                   # AI Agents
│   │   │   ├── __init__.py
│   │   │   ├── router_agent.py      # Main routing agent
│   │   │   ├── search_agent.py       # Paper search agent
│   │   │   ├── qa_agent.py          # Q&A agent (RAG)
│   │   │   └── summarization_agent.py
│   │   │
│   │   ├── chains/                   # LangChain Chains
│   │   │   ├── __init__.py
│   │   │   ├── vector_store.py      # Vector DB manager
│   │   │   ├── rag_chain.py         # RAG implementation
│   │   │   ├── citation_chain.py     # Citation generation
│   │   │   └── summarization_chain.py
│   │   │
│   │   ├── tools/                    # Agent Tools
│   │   │   ├── __init__.py
│   │   │   ├── arxiv_tool.py        # ArXiv search tool
│   │   │   ├── pdf_tool.py           # PDF processing tool
│   │   │   └── search_tool.py       # Unified search tool
│   │   │
│   │   ├── loaders/                  # Document Loaders
│   │   │   ├── __init__.py
│   │   │   ├── arxiv_loader.py      # ArXiv paper loader
│   │   │   └── pdf_loader.py        # PDF document loader
│   │   │
│   │   ├── api/                      # API Layer
│   │   │   ├── routes/              # API routes
│   │   │   │   ├── __init__.py
│   │   │   │   ├── search.py        # Search endpoints
│   │   │   │   ├── chat.py          # Chat/Q&A endpoints
│   │   │   │   └── papers.py        # Paper management endpoints
│   │   │   └── models/              # API schemas
│   │   │       ├── __init__.py
│   │   │       └── schemas.py       # Pydantic schemas
│   │   │
│   │   ├── config/                   # Configuration
│   │   │   ├── __init__.py
│   │   │   └── settings.py          # Pydantic settings
│   │   │
│   │   ├── prompts/                  # Prompt Templates
│   │   │   ├── __init__.py
│   │   │   ├── prompt_manager.py   # Prompt loader utility
│   │   │   ├── system_prompt.txt
│   │   │   ├── search_prompt.txt
│   │   │   ├── qa_prompt.txt
│   │   │   ├── summarization_prompt.txt
│   │   │   └── citation_prompt.txt
│   │   │
│   │   ├── utils/                    # Utilities
│   │   │   ├── __init__.py
│   │   │   ├── logger.py            # Logging setup
│   │   │   ├── validators.py        # Input validation
│   │   │   └── formatters.py        # Data formatting
│   │   │
│   │   ├── callbacks/                # LangChain callbacks (empty)
│   │   └── memory/                   # Memory management (empty)
│   │
│   ├── tests/                        # Test Suite
│   │   ├── __init__.py
│   │   ├── conftest.py              # Pytest fixtures
│   │   ├── unit/                    # Unit tests
│   │   │   ├── __init__.py
│   │   │   ├── test_agents.py
│   │   │   ├── test_chains.py
│   │   │   ├── test_loaders.py
│   │   │   └── test_tools.py
│   │   ├── integration/             # Integration tests
│   │   │   ├── __init__.py
│   │   │   └── test_workflows.py
│   │   └── e2e/                     # End-to-end tests
│   │       └── __init__.py
│   │
│   ├── scripts/                      # Utility Scripts
│   │   ├── setup_directories.ps1
│   │   ├── start_server.ps1
│   │   ├── test_api.ps1
│   │   └── run_tests.ps1
│   │
│   ├── data/                         # Local Data Storage
│   │   └── chroma/                  # Chroma vector DB data
│   │       └── chroma.sqlite3
│   │
│   ├── logs/                         # Application Logs
│   │   └── app.log
│   │
│   ├── requirements.txt              # Python dependencies
│   ├── pytest.ini                    # Pytest configuration
│   ├── README.md                     # Backend documentation
│   └── .env.example                 # Environment template
│
├── frontend/                         # Frontend (React.js/Streamlit)
│   └── README.md                    # Frontend setup guide
│
├── venv/                            # Python virtual environment (root)
│
├── docker-compose.yml               # Full stack deployment
├── .gitignore                       # Git ignore rules
├── .cursorrules                     # Cursor AI rules
├── README.md                        # Main project README
├── FRONTEND_COMPARISON.md           # Frontend framework comparison
├── QUICK_START.md                   # Quick start guide
├── TESTING_GUIDE.md                 # Testing documentation
└── PROJECT_STRUCTURE.md             # This file
```

## 🔄 File Organization Logic

### Backend (`backend/`)
- **All Python code** in `src/`
- **Tests** in `tests/` (mirrors `src/` structure)
- **Scripts** in `scripts/`
- **Data** in `data/` (local storage)
- **Logs** in `logs/`
- **Config** files at root level

### Frontend (`frontend/`)
- **Ready for setup** - Choose React.js or Streamlit
- **Will contain** frontend-specific code

### Root Level
- **Docker** configuration
- **Documentation** files
- **Virtual environment** (shared or separate)

## 📝 Important Paths

### Backend Entry Point
```
backend/src/main.py
```

### Backend Tests
```
backend/tests/
```

### Backend Scripts
```
backend/scripts/
```

### Frontend (Future)
```
frontend/src/        # React.js
frontend/pages/      # Streamlit
```

## 🚀 Running the Project

### Backend
```bash
cd backend
uvicorn src.main:app --reload
```

### Frontend (Future)
```bash
cd frontend
npm run dev          # React.js
# OR
streamlit run main.py # Streamlit
```

### Full Stack (Docker)
```bash
docker-compose up
```

## 📦 Dependencies

### Backend
- `backend/requirements.txt` - Python packages

### Frontend (Future)
- `frontend/package.json` - Node.js packages (React.js)
- `frontend/requirements.txt` - Python packages (Streamlit)

---

**Last Updated**: Project reorganization complete ✅


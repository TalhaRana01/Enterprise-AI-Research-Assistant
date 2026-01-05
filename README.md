# AI Research Assistant 🔍

An enterprise-grade AI-powered research assistant that helps researchers, students, and professionals find, analyze, and summarize academic papers and research materials.

## 🏗️ Project Structure

```
ai-research-assistant/
├── backend/                    # FastAPI Backend
│   ├── src/                    # Source code
│   │   ├── main.py            # FastAPI app entry point
│   │   ├── agents/            # AI agents
│   │   ├── chains/            # LangChain chains
│   │   ├── tools/             # Agent tools
│   │   ├── loaders/           # Document loaders
│   │   ├── api/               # API routes
│   │   ├── config/            # Configuration
│   │   ├── prompts/           # Prompt templates
│   │   └── utils/             # Utilities
│   ├── tests/                 # Test suite
│   ├── scripts/               # Utility scripts
│   ├── data/                  # Local data storage
│   ├── logs/                  # Application logs
│   ├── requirements.txt       # Python dependencies
│   └── pytest.ini             # Pytest configuration
│
├── frontend/                   # Frontend (React.js/Streamlit)
│   └── README.md              # Frontend setup guide
│
├── docker-compose.yml          # Full stack deployment
├── .gitignore                  # Git ignore rules
├── .cursorrules                # Cursor AI rules
└── README.md                   # This file
```

## ✨ Features

- 🔍 **Multi-Source Search**: Search across ArXiv, PubMed, Google Scholar, and more
- 📄 **Smart Summarization**: AI-powered paper summaries with key insights
- 📚 **Citation Management**: Automatic citation generation in multiple formats
- 💬 **Interactive Q&A**: Ask questions about papers and get contextual answers
- 🎯 **Semantic Search**: Find relevant papers based on meaning, not just keywords
- 📊 **Research Insights**: Extract key findings, methodologies, and conclusions
- 🔗 **Reference Tracking**: Track citations and related papers
- 📥 **Export Options**: Export summaries, notes, and citations

## 🛠️ Tech Stack

### Backend
- **Framework**: FastAPI 0.109+
- **AI Framework**: LangChain 0.1.0+
- **LLM**: OpenAI GPT-4 / GPT-3.5-turbo
- **Vector DB**: Pinecone (production) / Chroma (development)
- **Embeddings**: OpenAI text-embedding-3-small
- **Database**: PostgreSQL 14+
- **Cache**: Redis 7.0+
- **Monitoring**: LangSmith + Prometheus + Grafana

### Frontend
- **Framework**: React.js (recommended) or Streamlit
- **Status**: 🚧 In Development

## 🚀 Quick Start

### Prerequisites
- Python 3.10+
- Node.js 18+ (for React.js frontend)
- Docker & Docker Compose (optional)

### Backend Setup

```bash
# Navigate to backend directory
cd backend

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Setup environment variables
cp .env.example .env
# Edit .env with your API keys

# Run the backend server
uvicorn src.main:app --reload --port 8000
```

### Frontend Setup

**React.js (Recommended):**
```bash
cd frontend
npm install
npm run dev
```

**Streamlit:**
```bash
cd frontend
pip install -r requirements.txt
streamlit run main.py
```

### Docker Setup (Full Stack)

```bash
# Start all services
docker-compose up --build

# Backend API: http://localhost:8000
# Frontend: http://localhost:3000
# API Docs: http://localhost:8000/docs
```

## 📡 API Endpoints

### Search Papers
```bash
GET /api/v1/search?query=transformer+models&max_results=10
POST /api/v1/search
{
  "query": "transformer models in NLP",
  "max_results": 10
}
```

### Chat/Q&A
```bash
POST /api/v1/chat
{
  "question": "What are the key findings?",
  "paper_ids": ["arxiv:2301.12345"]
}

POST /api/v1/chat/stream  # Streaming response
```

### Papers Management
```bash
POST /api/v1/papers/summarize
GET /api/v1/papers/{paper_id}/summarize
POST /api/v1/papers/cite
GET /api/v1/papers/{paper_id}
```

### Health Check
```bash
GET /health
```

## 📁 Directory Structure Details

### Backend (`backend/`)
- **`src/agents/`**: AI agents (Search, Q&A, Summarization, Router)
- **`src/chains/`**: LangChain chains (RAG, Citation, Summarization)
- **`src/tools/`**: Agent tools (ArXiv, PDF, Search)
- **`src/loaders/`**: Document loaders (ArXiv, PDF)
- **`src/api/`**: FastAPI routes and schemas
- **`src/config/`**: Configuration management
- **`src/prompts/`**: Prompt templates
- **`tests/`**: Unit, integration, and E2E tests

### Frontend (`frontend/`)
- **Status**: 🚧 Ready for React.js or Streamlit setup
- See `FRONTEND_COMPARISON.md` for options

## 🔧 Configuration

### Backend Environment Variables

Create `backend/.env`:

```env
# Environment
ENVIRONMENT=development
DEBUG=true

# API Configuration
API_V1_PREFIX=/api/v1
SECRET_KEY=your-secret-key-here

# OpenAI
OPENAI_API_KEY=your-openai-key-here
LLM_MODEL=gpt-4
EMBEDDING_MODEL=text-embedding-3-small

# Vector Database
VECTOR_DB_TYPE=chroma  # or pinecone
CHROMA_PERSIST_DIRECTORY=./data/chroma

# Pinecone (if using)
PINECONE_API_KEY=your-pinecone-key
PINECONE_INDEX_NAME=research-papers

# Database
DATABASE_URL=postgresql://user:pass@localhost:5432/research_db

# Redis
REDIS_URL=redis://localhost:6379/0

# Monitoring
LANGCHAIN_TRACING_V2=true
LANGCHAIN_PROJECT=ai-research-assistant
LANGCHAIN_API_KEY=your-langsmith-key
```

## 🧪 Testing

```bash
cd backend

# Run all tests
pytest

# Run with coverage
pytest --cov=src --cov-report=html

# Run specific test file
pytest tests/unit/test_agents.py -v
```

## 📚 Documentation

- **Backend API Docs**: http://localhost:8000/docs (Swagger UI)
- **Testing Guide**: `backend/TESTING_GUIDE.md`
- **Frontend Comparison**: `FRONTEND_COMPARISON.md`
- **Quick Start**: `QUICK_START.md`

## 🏗️ Architecture

```
┌─────────────────┐
│   Frontend       │
│   (React.js)     │
└────────┬─────────┘
         │ HTTP/REST
    ┌────▼─────┐
    │  Backend │
    │ (FastAPI)│
    └────┬─────┘
         │
    ┌────┴────────────────────┐
    │                         │
┌───▼────────┐      ┌────────▼─────┐
│  Router    │      │  Q&A Agent   │
│  Agent     │      │  (RAG)       │
└───┬────────┘      └────────┬─────┘
    │                        │
┌───▼────────┐      ┌────────▼─────┐
│ ArXiv API  │      │  Vector DB   │
│ PubMed API │      │  (Pinecone)  │
└────────────┘      └──────────────┘
```

## 🚧 Roadmap

### Phase 1 (Completed) ✅
- [x] Backend API with FastAPI
- [x] LangChain agents and chains
- [x] ArXiv integration
- [x] RAG system
- [x] Basic testing

### Phase 2 (In Progress) 🚧
- [ ] Frontend (React.js)
- [ ] User authentication
- [ ] Advanced search filters
- [ ] Citation management UI

### Phase 3 (Planned) 📋
- [ ] Multi-source search (PubMed, Scholar)
- [ ] User profiles and saved papers
- [ ] Collaborative features
- [ ] Mobile app (React Native)

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 📝 License

This project is licensed under the MIT License.

## 🙏 Acknowledgments

- LangChain for the AI framework
- OpenAI for LLM capabilities
- FastAPI for the web framework
- ArXiv for research paper access

---

**Built with ❤️ for the research community**

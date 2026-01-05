# Backend - AI Research Assistant API

FastAPI-based backend for the AI Research Assistant application.

## 🚀 Quick Start

```bash
# Activate virtual environment
source venv/bin/activate  # Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Setup environment
cp .env.example .env
# Edit .env with your API keys

# Run server
uvicorn src.main:app --reload --port 8000
```

## 📁 Structure

```
backend/
├── src/
│   ├── main.py              # FastAPI app entry point
│   ├── agents/              # AI agents
│   ├── chains/              # LangChain chains
│   ├── tools/               # Agent tools
│   ├── loaders/             # Document loaders
│   ├── api/                 # API routes & schemas
│   ├── config/              # Configuration
│   ├── prompts/             # Prompt templates
│   └── utils/               # Utilities
├── tests/                   # Test suite
├── scripts/                 # Utility scripts
├── data/                    # Local data storage
├── logs/                    # Application logs
├── requirements.txt         # Dependencies
└── pytest.ini              # Test configuration
```

## 🔧 Configuration

See `.env.example` for all configuration options.

## 🧪 Testing

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=src --cov-report=html

# Run specific test
pytest tests/unit/test_agents.py -v
```

## 📡 API Endpoints

- **Health**: `GET /health`
- **Search**: `GET/POST /api/v1/search`
- **Chat**: `POST /api/v1/chat`
- **Papers**: `POST /api/v1/papers/*`
- **Docs**: `GET /docs` (Swagger UI)

## 📚 Documentation

- **API Docs**: http://localhost:8000/docs
- **Testing Guide**: `TESTING_GUIDE.md`


# AI Research Assistant 🔍

An enterprise-grade AI-powered research assistant that helps researchers, students, and professionals find, analyze, and summarize academic papers and research materials.

## Features

- 🔍 **Multi-Source Search**: Search across ArXiv, PubMed, Google Scholar, and more
- 📄 **Smart Summarization**: AI-powered paper summaries with key insights
- 📚 **Citation Management**: Automatic citation generation in multiple formats
- 💬 **Interactive Q&A**: Ask questions about papers and get contextual answers
- 🎯 **Semantic Search**: Find relevant papers based on meaning, not just keywords
- 📊 **Research Insights**: Extract key findings, methodologies, and conclusions
- 🔗 **Reference Tracking**: Track citations and related papers
- 📥 **Export Options**: Export summaries, notes, and citations

## Tech Stack

- **Framework**: LangChain 0.1.0+
- **LLM**: OpenAI GPT-4 / GPT-3.5-turbo
- **Vector DB**: Pinecone (or Chroma for local development)
- **Embeddings**: OpenAI text-embedding-3-small
- **API Framework**: FastAPI 0.104+
- **Database**: PostgreSQL 14+
- **Cache**: Redis 7.0+
- **Monitoring**: LangSmith + Prometheus + Grafana

## Architecture

```
┌─────────────────┐
│   User Query    │
└────────┬────────┘
         │
    ┌────▼─────┐
    │  Router  │
    │  Agent   │
    └────┬─────┘
         │
    ┌────┴────────────────────┐
    │                         │
┌───▼────────┐      ┌────────▼─────┐
│  Search    │      │  Q&A Agent   │
│  Agent     │      │  (RAG)       │
└───┬────────┘      └────────┬─────┘
    │                        │
┌───▼────────┐      ┌────────▼─────┐
│ ArXiv API  │      │  Vector DB   │
│ PubMed API │      │  (Pinecone)  │
│ Scholar API│      │              │
└────────────┘      └──────────────┘
         │                  │
    ┌────▼──────────────────▼────┐
    │   Summarization Agent      │
    └────┬───────────────────────┘
         │
    ┌────▼────────┐
    │  Response   │
    └─────────────┘
```

## Project Structure

```
ai-research-assistant/
├── .env.development
├── .env.production
├── .gitignore
├── requirements.txt
├── docker-compose.yml
├── README.md
├── src/
│   ├── __init__.py
│   ├── main.py                 # FastAPI app entry point
│   ├── config/
│   │   ├── __init__.py
│   │   └── settings.py         # Configuration management
│   ├── agents/
│   │   ├── __init__.py
│   │   ├── router_agent.py     # Main routing agent
│   │   ├── search_agent.py     # Paper search agent
│   │   ├── qa_agent.py         # Question answering agent
│   │   └── summarization_agent.py
│   ├── chains/
│   │   ├── __init__.py
│   │   ├── rag_chain.py        # RAG implementation
│   │   └── citation_chain.py   # Citation generation
│   ├── tools/
│   │   ├── __init__.py
│   │   ├── arxiv_tool.py       # ArXiv search tool
│   │   ├── pubmed_tool.py      # PubMed search tool
│   │   └── pdf_tool.py         # PDF processing tool
│   ├── loaders/
│   │   ├── __init__.py
│   │   ├── arxiv_loader.py     # ArXiv paper loader
│   │   └── pdf_loader.py       # PDF document loader
│   ├── prompts/
│   │   ├── system_prompt.txt
│   │   ├── search_prompt.txt
│   │   ├── summarization_prompt.txt
│   │   └── qa_prompt.txt
│   ├── memory/
│   │   ├── __init__.py
│   │   └── conversation_memory.py
│   ├── callbacks/
│   │   ├── __init__.py
│   │   ├── cost_tracking.py
│   │   └── monitoring.py
│   ├── utils/
│   │   ├── __init__.py
│   │   ├── logger.py
│   │   ├── validators.py
│   │   └── formatters.py
│   └── api/
│       ├── __init__.py
│       ├── routes/
│       │   ├── __init__.py
│       │   ├── search.py
│       │   ├── chat.py
│       │   └── papers.py
│       └── models/
│           ├── __init__.py
│           └── schemas.py
├── tests/
│   ├── __init__.py
│   ├── unit/
│   │   ├── test_agents.py
│   │   ├── test_chains.py
│   │   └── test_tools.py
│   ├── integration/
│   │   ├── test_api.py
│   │   └── test_workflows.py
│   └── e2e/
│       └── test_research_flow.py
├── docs/
│   ├── architecture.md
│   ├── api.md
│   └── deployment.md
└── scripts/
    ├── setup.sh
    ├── run_dev.sh
    └── deploy.sh
```

## Quick Start

### Prerequisites

- Python 3.10+
- PostgreSQL 14+
- Redis 7.0+
- OpenAI API key
- Pinecone API key (or use Chroma locally)

### Installation

```bash
# Clone the repository
git clone <your-repo-url>
cd ai-research-assistant

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Setup environment variables
cp .env.development .env
# Edit .env with your API keys

# Run database migrations
python scripts/setup.sh

# Start the application
python src/main.py
```

### Development

```bash
# Run in development mode with hot reload
uvicorn src.main:app --reload --port 8000

# Run tests
pytest tests/ -v --cov=src

# Run linting
black src/ tests/
flake8 src/ tests/
mypy src/
```

### Docker

```bash
# Build and run with Docker Compose
docker-compose up --build

# Access the API
curl http://localhost:8000/docs
```

## API Endpoints

### Search Papers
```bash
POST /api/v1/search
{
  "query": "transformer models in NLP",
  "sources": ["arxiv", "pubmed"],
  "limit": 10
}
```

### Chat with Papers
```bash
POST /api/v1/chat
{
  "message": "What are the key findings?",
  "paper_ids": ["arxiv:2301.12345"],
  "session_id": "user-123"
}
```

### Summarize Paper
```bash
POST /api/v1/summarize
{
  "paper_id": "arxiv:2301.12345",
  "format": "detailed"
}
```

## Configuration

Key configuration options in `.env`:

```bash
# LLM Configuration
OPENAI_API_KEY=your-key-here
LLM_MODEL=gpt-4
EMBEDDING_MODEL=text-embedding-3-small

# Vector Database
PINECONE_API_KEY=your-key-here
PINECONE_ENVIRONMENT=us-west1-gcp
PINECONE_INDEX_NAME=research-papers

# Database
DATABASE_URL=postgresql://user:pass@localhost:5432/research_db

# Redis
REDIS_URL=redis://localhost:6379

# Monitoring
LANGCHAIN_TRACING_V2=true
LANGCHAIN_PROJECT=ai-research-assistant
LANGCHAIN_API_KEY=your-langsmith-key
```

## Features Roadmap

### Phase 1 (Week 1-2) - MVP
- [x] Basic RAG system
- [x] ArXiv integration
- [x] Simple Q&A
- [x] PDF processing
- [x] Basic API

### Phase 2 (Week 3-4) - Enhanced
- [ ] Multi-source search (PubMed, Scholar)
- [ ] Citation management
- [ ] Advanced summarization
- [ ] User authentication
- [ ] Session management

### Phase 3 (Week 5-6) - Advanced
- [ ] Multi-agent orchestration
- [ ] Research insights extraction
- [ ] Collaborative features
- [ ] Export options
- [ ] Analytics dashboard

### Phase 4 (Future)
- [ ] Mobile app
- [ ] Browser extension
- [ ] Zotero/Mendeley integration
- [ ] Team collaboration
- [ ] Custom research workflows

## Performance Metrics

- **Response Time**: < 2s for search, < 5s for summarization
- **Accuracy**: 90%+ relevant results
- **Cost**: ~$0.05 per research query
- **Uptime**: 99.9% SLA

## Contributing

See [CONTRIBUTING.md](CONTRIBUTING.md) for guidelines.

## License

MIT License - see [LICENSE](LICENSE) for details.

## Support

- Documentation: [docs/](docs/)
- Issues: GitHub Issues
- Email mtalharana093@gmail.com

## Acknowledgments

Built with:
- [LangChain](https://langchain.com)
- [OpenAI](https://openai.com)
- [Pinecone](https://pinecone.io)
- [FastAPI](https://fastapi.tiangolo.com)

---

**Made with ❤️ for researchers worldwide**


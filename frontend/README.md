# Frontend - AI Research Assistant

Frontend application for the AI Research Assistant.

## 🎯 Status

🚧 **Ready for Setup**

Choose your framework:
- **React.js** (Recommended for production)
- **Streamlit** (Quick prototype)

## 📋 Next Steps

1. **Choose Framework**: See `../FRONTEND_COMPARISON.md` for comparison
2. **Setup**: Follow framework-specific setup guide
3. **Connect**: Configure API endpoint to `http://localhost:8000`

## 🔗 API Integration

Backend API runs on: `http://localhost:8000`

### Key Endpoints:
- `GET /api/v1/search` - Search papers
- `POST /api/v1/chat` - Q&A chat
- `POST /api/v1/papers/summarize` - Summarize papers
- `GET /health` - Health check

## 📁 Structure (React.js)

```
frontend/
├── src/
│   ├── components/      # UI components
│   ├── pages/           # Page components
│   ├── services/        # API clients
│   ├── hooks/           # Custom hooks
│   ├── store/           # State management
│   └── types/           # TypeScript types
├── public/
├── package.json
└── README.md
```

## 📁 Structure (Streamlit)

```
frontend/
├── pages/               # Multi-page app
├── components/          # Reusable components
├── utils/               # Helper functions
├── main.py              # Main app
└── requirements.txt
```

---

**Ready to start?** Choose your framework and begin setup! 🚀


# Testing Guide - AI Research Assistant

## 🧪 Testing Setup Complete!

Maine aapke liye complete testing infrastructure setup kar diya hai.

---

## 📁 Test Files Created

### ✅ Test Structure:
```
tests/
├── __init__.py
├── conftest.py              # Shared fixtures & configuration
├── README.md                # Testing documentation
├── unit/                    # Unit tests
│   ├── test_loaders.py      # Loader tests
│   ├── test_tools.py        # Tool tests
│   ├── test_chains.py       # Chain tests
│   └── test_agents.py       # Agent tests
├── integration/             # Integration tests
│   └── test_workflows.py    # Workflow tests
└── e2e/                     # End-to-end tests
    └── (ready for E2E tests)
```

### ✅ Configuration Files:
- `pytest.ini` - Pytest configuration
- `scripts/run_tests.ps1` - Test runner script

---

## 🚀 Quick Start

### Step 1: Install Dependencies

```powershell
# Activate virtual environment
.\venv\Scripts\activate

# Install pytest and testing dependencies
pip install pytest pytest-cov pytest-mock pytest-asyncio
```

Ya phir:

```powershell
pip install -r requirements.txt
```

### Step 2: Run Tests

#### Option A: Using Script (Easy)
```powershell
.\scripts\run_tests.ps1
```

#### Option B: Direct Command
```powershell
# Run all tests
pytest tests/ -v

# Run with coverage
pytest tests/ --cov=src --cov-report=html

# Run specific test file
pytest tests/unit/test_loaders.py -v

# Run specific test
pytest tests/unit/test_loaders.py::TestArXivLoader::test_search_success -v
```

---

## 📊 Test Coverage

### Current Test Files:

1. **test_loaders.py** - Tests for:
   - ArXivLoader (search, load_by_id, conversion)
   - PDFLoader (load, extract_text)

2. **test_tools.py** - Tests for:
   - arxiv_search_tool
   - search_papers_tool
   - pdf_process_tool

3. **test_chains.py** - Tests for:
   - VectorStore (init, add_documents, search)
   - RAGChain (initialization)
   - CitationChain (citation generation)
   - SummarizationChain (initialization)

4. **test_agents.py** - Tests for:
   - SearchAgent (init, search)
   - QAAgent (init, answer)
   - RouterAgent (routing logic)

---

## 🎯 Test Commands

### Basic Commands:
```bash
# Run all tests
pytest

# Verbose output
pytest -v

# Show print statements
pytest -s

# Run only unit tests
pytest tests/unit/

# Run only integration tests
pytest tests/integration/ -m integration

# Run with coverage report
pytest --cov=src --cov-report=term-missing

# Generate HTML coverage report
pytest --cov=src --cov-report=html
# Then open: htmlcov/index.html
```

### Advanced Commands:
```bash
# Run tests matching pattern
pytest -k "test_search"

# Run tests in parallel (faster)
pytest -n auto

# Stop on first failure
pytest -x

# Show local variables on failure
pytest -l

# Run last failed tests only
pytest --lf
```

---

## 🔍 Understanding Test Results

### Success Output:
```
tests/unit/test_loaders.py::TestArXivLoader::test_search_success PASSED
tests/unit/test_tools.py::TestArXivSearchTool::test_arxiv_search_tool_success PASSED
```

### Failure Output:
```
FAILED tests/unit/test_loaders.py::TestArXivLoader::test_search_success
AssertionError: Expected 1, got 0
```

### Coverage Report:
```
Name                    Stmts   Miss  Cover
-------------------------------------------
src/loaders/arxiv.py      150     20    87%
src/tools/search.py        80     10    88%
```

---

## 🛠️ Writing New Tests

### Example Test Structure:
```python
import pytest
from unittest.mock import Mock, patch
from src.loaders import ArXivLoader

class TestArXivLoader:
    """Test ArXivLoader class."""
    
    @patch("src.loaders.arxiv_loader.LangChainArxivLoader")
    def test_search_success(self, mock_loader_class):
        """Test successful paper search."""
        # Setup
        mock_loader = Mock()
        mock_loader.load.return_value = [mock_doc]
        mock_loader_class.return_value = mock_loader
        
        # Test
        loader = ArXivLoader()
        results = loader.search("test query")
        
        # Assert
        assert len(results) == 1
        assert results[0]["title"] == "Test Paper"
```

---

## 📝 Test Best Practices

1. **Use Mocks**: Mock external APIs (OpenAI, ArXiv)
2. **Isolate Tests**: Each test should be independent
3. **Clear Names**: Test names should describe what they test
4. **Arrange-Act-Assert**: Follow AAA pattern
5. **Test Edge Cases**: Test errors, empty inputs, etc.

---

## 🐛 Common Issues

### Issue 1: Module Not Found
```bash
# Solution: Install dependencies
pip install -r requirements.txt
```

### Issue 2: Import Errors
```bash
# Solution: Run from project root
cd D:\Agentic_AI_Projects
pytest
```

### Issue 3: Mock Not Working
```bash
# Solution: Check import path in patch decorator
@patch("src.loaders.arxiv_loader.LangChainArxivLoader")
```

---

## 📈 Coverage Goals

- **Current**: ~60% (with mocks)
- **Target**: 80%+
- **Critical Paths**: 100% (loaders, chains, agents)

---

## 🎓 Next Steps

1. ✅ Install pytest: `pip install pytest pytest-cov`
2. ✅ Run tests: `pytest tests/ -v`
3. ✅ Check coverage: `pytest --cov=src --cov-report=html`
4. ✅ Add more tests as you develop
5. ✅ Run tests before committing code

---

## 💡 Tips

- Run tests frequently during development
- Fix failing tests before adding new features
- Aim for high coverage on critical components
- Use integration tests for workflows
- Use E2E tests for user journeys

---

**Happy Testing! 🚀**


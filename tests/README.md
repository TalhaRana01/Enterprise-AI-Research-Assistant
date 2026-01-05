# Testing Guide

## Running Tests

### Run all tests
```bash
pytest
```

### Run specific test file
```bash
pytest tests/unit/test_loaders.py
```

### Run with coverage
```bash
pytest --cov=src --cov-report=html
```

### Run specific test class
```bash
pytest tests/unit/test_loaders.py::TestArXivLoader
```

### Run specific test function
```bash
pytest tests/unit/test_loaders.py::TestArXivLoader::test_search_success
```

## Test Structure

```
tests/
├── __init__.py
├── conftest.py          # Shared fixtures
├── unit/                # Unit tests
│   ├── test_loaders.py
│   ├── test_tools.py
│   ├── test_chains.py
│   └── test_agents.py
├── integration/         # Integration tests
│   └── test_workflows.py
└── e2e/                 # End-to-end tests
    └── (to be added)
```

## Test Categories

- **Unit Tests**: Test individual components in isolation
- **Integration Tests**: Test component interactions
- **E2E Tests**: Test complete user workflows

## Mocking

Tests use mocks to avoid:
- External API calls (OpenAI, ArXiv)
- File system operations
- Network requests

## Coverage Goal

Target: 80%+ code coverage

## Running Tests in CI/CD

Tests run automatically on:
- Pull requests
- Commits to main branch
- Manual trigger


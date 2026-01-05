"""API routes."""

from .search import router as search_router
from .chat import router as chat_router
from .papers import router as papers_router
from .auth import router as auth_router

__all__ = ["search_router", "chat_router", "papers_router", "auth_router"]


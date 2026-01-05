"""Chat/Q&A endpoints for asking questions about research papers."""

from fastapi import APIRouter, HTTPException
from typing import Optional

from src.api.models.schemas import ChatRequest, ChatResponse, PaperInfo, ErrorResponse
from src.agents import QAAgent, create_qa_agent
from src.utils.logger import get_logger

logger = get_logger(__name__)

router = APIRouter(prefix="/api/v1/chat", tags=["chat"])

# Initialize Q&A agent (singleton pattern)
_qa_agent: Optional[QAAgent] = None


def get_qa_agent() -> QAAgent:
    """Get or create Q&A agent instance."""
    global _qa_agent
    if _qa_agent is None:
        _qa_agent = create_qa_agent(verbose=False)
    return _qa_agent


@router.post("", response_model=ChatResponse)
async def chat(request: ChatRequest):
    """
    Ask a question about research papers.
    
    This endpoint uses RAG (Retrieval-Augmented Generation) to answer
    questions based on papers in the vector database.
    
    **Example Request:**
    ```json
    {
        "question": "What is transformer architecture?",
        "paper_ids": ["arxiv:2301.12345"],
        "session_id": "user-123"
    }
    ```
    
    **Example Response:**
    ```json
    {
        "answer": "Transformer architecture is...",
        "question": "What is transformer architecture?",
        "sources": [
            {
                "id": "arxiv:2301.12345",
                "title": "Attention Is All You Need",
                "authors": ["Vaswani", "Shazeer"],
                "source": "arxiv"
            }
        ],
        "num_sources": 1,
        "session_id": "user-123"
    }
    ```
    """
    try:
        logger.info(f"Chat request: question='{request.question[:50]}...', session_id={request.session_id}")
        
        # Get Q&A agent
        agent = get_qa_agent()
        
        # Answer question
        result = agent.answer(
            question=request.question,
            paper_ids=request.paper_ids
        )
        
        # Convert sources to PaperInfo objects
        sources = [
            PaperInfo(
                id=source.get("id", ""),
                title=source.get("title", ""),
                authors=source.get("authors", "").split(", ") if isinstance(source.get("authors"), str) else source.get("authors", []),
                published=source.get("published"),
                source=source.get("source", "unknown")
            )
            for source in result.get("sources", [])
        ]
        
        response = ChatResponse(
            answer=result.get("answer", ""),
            question=request.question,
            sources=sources,
            num_sources=result.get("num_sources", len(sources)),
            session_id=request.session_id
        )
        
        logger.info(f"Chat completed: answer generated with {len(sources)} sources")
        return response
        
    except ValueError as e:
        logger.error(f"Validation error in chat: {e}")
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Chat failed: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to generate answer: {str(e)}"
        )


@router.post("/stream")
async def chat_stream(request: ChatRequest):
    """
    Stream answer as it's generated (Server-Sent Events).
    
    This endpoint streams the answer token by token as it's generated,
    providing a better user experience for long responses.
    
    **Example:**
    ```
    POST /api/v1/chat/stream
    {
        "question": "Explain transformer architecture"
    }
    ```
    
    Returns: Stream of text chunks
    """
    try:
        logger.info(f"Stream chat request: question='{request.question[:50]}...'")
        
        # Get Q&A agent
        agent = get_qa_agent()
        
        # Stream answer
        from fastapi.responses import StreamingResponse
        
        async def generate_stream():
            try:
                for chunk in agent.stream_answer(request.question):
                    yield f"data: {chunk}\n\n"
            except Exception as e:
                logger.error(f"Streaming error: {e}")
                yield f"data: Error: {str(e)}\n\n"
        
        return StreamingResponse(
            generate_stream(),
            media_type="text/event-stream"
        )
        
    except Exception as e:
        logger.error(f"Stream chat failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))


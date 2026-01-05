"""RAG (Retrieval-Augmented Generation) chain for answering questions about research papers."""

from typing import Dict, Any, Optional, List
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain_core.runnables import RunnablePassthrough
from langchain_openai import ChatOpenAI
from langchain_core.documents import Document

from src.utils.logger import get_logger
from src.config import settings
from src.prompts import load_prompt
from .vector_store import VectorStore, get_vector_store

logger = get_logger(__name__)


def format_docs(docs: List[Document]) -> str:
    """
    Format retrieved documents for context.
    
    Args:
        docs: List of Document objects
        
    Returns:
        Formatted context string
    """
    formatted = []
    
    for i, doc in enumerate(docs, 1):
        title = doc.metadata.get("title", "Unknown Title")
        authors = doc.metadata.get("authors", "Unknown Authors")
        source = doc.metadata.get("source", "unknown")
        
        formatted.append(
            f"[Document {i}]\n"
            f"Title: {title}\n"
            f"Authors: {authors}\n"
            f"Source: {source}\n"
            f"Content: {doc.page_content[:500]}...\n"
        )
    
    return "\n\n".join(formatted)


class RAGChain:
    """
    RAG Chain for question-answering about research papers.
    
    Flow:
    1. User asks a question
    2. Search relevant papers in vector store
    3. Retrieve top-k most relevant documents
    4. Format context from documents
    5. Generate answer using LLM with context
    """
    
    def __init__(
        self,
        vector_store: Optional[VectorStore] = None,
        llm_model: Optional[str] = None,
        k: int = 5
    ):
        """
        Initialize RAG chain.
        
        Args:
            vector_store: Vector store instance (default: global instance)
            llm_model: LLM model name (default: from settings)
            k: Number of documents to retrieve
        """
        self.vector_store = vector_store or get_vector_store()
        self.llm_model = llm_model or settings.llm_model
        self.k = k
        
        logger.info(f"Initializing RAGChain: model={self.llm_model}, k={k}")
        
        # Initialize LLM
        self.llm = ChatOpenAI(
            model=self.llm_model,
            temperature=settings.llm_temperature,
            max_tokens=settings.llm_max_tokens,
            openai_api_key=settings.openai_api_key,
            request_timeout=settings.request_timeout
        )
        
        # Load Q&A prompt template
        try:
            prompt_template = load_prompt("qa_prompt")
        except Exception as e:
            logger.warning(f"Failed to load qa_prompt, using default: {e}")
            prompt_template = """Use the following context from research papers to answer the question.

Context: {context}

Question: {question}

Answer based on the context provided. If the answer is not in the context, say so."""
        
        # Create prompt template
        self.prompt = ChatPromptTemplate.from_template(prompt_template)
        
        # Get retriever
        self.retriever = self.vector_store.as_retriever(
            k=self.k,
            search_type="similarity"
        )
        
        # Build RAG chain using LCEL (LangChain Expression Language)
        self.chain = (
            {
                "context": self.retriever | format_docs,
                "question": RunnablePassthrough()
            }
            | self.prompt
            | self.llm
            | StrOutputParser()
        )
        
        logger.info("RAGChain initialized successfully")
    
    def invoke(self, question: str) -> Dict[str, Any]:
        """
        Answer a question using RAG.
        
        Args:
            question: User's question
            
        Returns:
            Dictionary with answer and metadata
        """
        try:
            logger.info(f"Processing question: '{question[:50]}...'")
            
            # Invoke chain
            answer = self.chain.invoke(question)
            
            # Get retrieved documents for context
            retrieved_docs = self.retriever.get_relevant_documents(question)
            
            result = {
                "answer": answer,
                "question": question,
                "sources": [
                    {
                        "title": doc.metadata.get("title", "Unknown"),
                        "authors": doc.metadata.get("authors", "Unknown"),
                        "source": doc.metadata.get("source", "unknown"),
                        "id": doc.metadata.get("id", "")
                    }
                    for doc in retrieved_docs
                ],
                "num_sources": len(retrieved_docs)
            }
            
            logger.info(f"Generated answer with {len(retrieved_docs)} sources")
            return result
            
        except Exception as e:
            logger.error(f"RAG chain invocation failed: {e}")
            raise Exception(f"Failed to generate answer: {str(e)}")
    
    def stream(self, question: str):
        """
        Stream answer as it's generated.
        
        Args:
            question: User's question
            
        Yields:
            Answer chunks as they're generated
        """
        try:
            logger.info(f"Streaming answer for: '{question[:50]}...'")
            
            for chunk in self.chain.stream(question):
                yield chunk
                
        except Exception as e:
            logger.error(f"RAG streaming failed: {e}")
            raise Exception(f"Streaming failed: {str(e)}")
    
    def batch(self, questions: List[str]) -> List[Dict[str, Any]]:
        """
        Process multiple questions in batch.
        
        Args:
            questions: List of questions
            
        Returns:
            List of answer dictionaries
        """
        try:
            logger.info(f"Processing batch of {len(questions)} questions")
            
            results = []
            for question in questions:
                try:
                    result = self.invoke(question)
                    results.append(result)
                except Exception as e:
                    logger.warning(f"Failed to process question '{question}': {e}")
                    results.append({
                        "answer": f"Error: {str(e)}",
                        "question": question,
                        "sources": [],
                        "num_sources": 0
                    })
            
            logger.info(f"Processed {len(results)} questions")
            return results
            
        except Exception as e:
            logger.error(f"Batch processing failed: {e}")
            raise Exception(f"Batch processing failed: {str(e)}")


def create_rag_chain(
    vector_store: Optional[VectorStore] = None,
    llm_model: Optional[str] = None,
    k: int = 5
) -> RAGChain:
    """
    Factory function to create a RAG chain.
    
    Args:
        vector_store: Vector store instance
        llm_model: LLM model name
        k: Number of documents to retrieve
        
    Returns:
        RAGChain instance
    """
    return RAGChain(
        vector_store=vector_store,
        llm_model=llm_model,
        k=k
    )


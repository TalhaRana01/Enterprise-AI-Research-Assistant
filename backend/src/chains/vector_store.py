"""Vector database setup and management for document storage and retrieval."""

from typing import List, Optional
from pathlib import Path
from langchain_core.documents import Document
from langchain_openai import OpenAIEmbeddings
from langchain_community.vectorstores import Chroma
try:
    from langchain_community.vectorstores import Pinecone as PineconeVectorStore
except ImportError:
    try:
        from langchain_pinecone import PineconeVectorStore
    except ImportError:
        PineconeVectorStore = None

# Optional pinecone import (only needed if using Pinecone)
# Note: Modern Pinecone SDK uses 'pinecone' package (not 'pinecone-client')
try:
    import pinecone
    from pinecone import Pinecone as PineconeClient
except ImportError:
    pinecone = None
    PineconeClient = None

from src.utils.logger import get_logger
from src.config import settings

logger = get_logger(__name__)


class VectorStore:
    """
    Vector database manager for storing and retrieving research papers.
    
    Supports:
    - Chroma (local development)
    - Pinecone (production)
    - Document storage and retrieval
    - Similarity search
    """
    
    def __init__(
        self,
        collection_name: Optional[str] = None,
        persist_directory: Optional[str] = None
    ):
        """
        Initialize vector store.
        
        Args:
            collection_name: Collection/index name
            persist_directory: Directory for Chroma persistence (local only)
        """
        self.vector_db_type = settings.vector_db_type.lower()
        self.collection_name = collection_name or "research_papers"
        
        logger.info(f"Initializing VectorStore: type={self.vector_db_type}")
        
        # Initialize embeddings
        self.embeddings = OpenAIEmbeddings(
            model=settings.embedding_model,
            openai_api_key=settings.openai_api_key
        )
        
        # Initialize vector store based on type
        if self.vector_db_type == "chroma":
            self._init_chroma(persist_directory)
        elif self.vector_db_type == "pinecone":
            self._init_pinecone()
        else:
            raise ValueError(f"Unsupported vector DB type: {self.vector_db_type}")
        
        logger.info(f"VectorStore initialized successfully: {self.vector_db_type}")
    
    def _init_chroma(self, persist_directory: Optional[str] = None) -> None:
        """Initialize Chroma vector store (local)."""
        try:
            persist_dir = persist_directory or settings.chroma_persist_directory
            
            # Create directory if it doesn't exist
            Path(persist_dir).mkdir(parents=True, exist_ok=True)
            
            # Initialize Chroma
            self.vectorstore = Chroma(
                collection_name=self.collection_name,
                embedding_function=self.embeddings,
                persist_directory=persist_dir
            )
            
            logger.info(f"Chroma initialized: {persist_dir}")
            
        except Exception as e:
            logger.error(f"Failed to initialize Chroma: {e}")
            raise Exception(f"Chroma initialization failed: {str(e)}")
    
    def _init_pinecone(self) -> None:
        """Initialize Pinecone vector store (production)."""
        try:
            if pinecone is None:
                raise ImportError("pinecone package not installed. Install with: pip install pinecone")
            
            if PineconeVectorStore is None:
                raise ImportError("PineconeVectorStore not available. Install langchain-pinecone or langchain-community")
            
            if not settings.pinecone_api_key:
                raise ValueError("Pinecone API key not configured")
            
            if not settings.pinecone_index_name:
                raise ValueError("Pinecone index name not configured")
            
            # Initialize Pinecone client (modern SDK v5+)
            index_name = settings.pinecone_index_name
            
            if PineconeClient:
                # Modern Pinecone SDK (v5+) - uses Pinecone() class
                pc = PineconeClient(api_key=settings.pinecone_api_key)
                
                # Check if index exists
                try:
                    indexes = [idx.name for idx in pc.list_indexes()]
                    if index_name not in indexes:
                        logger.warning(f"Index {index_name} not found. Please create it in Pinecone dashboard.")
                        raise ValueError(f"Pinecone index '{index_name}' does not exist")
                except Exception as e:
                    logger.error(f"Failed to list Pinecone indexes: {e}")
                    raise ValueError(f"Failed to connect to Pinecone: {str(e)}")
                
                # Initialize Pinecone vector store
                self.vectorstore = PineconeVectorStore(
                    index_name=index_name,
                    embedding=self.embeddings
                )
            elif pinecone:
                # Legacy Pinecone SDK (fallback for older versions)
                pinecone.init(
                    api_key=settings.pinecone_api_key,
                    environment=settings.pinecone_environment
                )
                
                # Check if index exists
                if index_name not in pinecone.list_indexes():
                    logger.warning(f"Index {index_name} not found. Please create it in Pinecone dashboard.")
                    raise ValueError(f"Pinecone index '{index_name}' does not exist")
                
                # Initialize Pinecone vector store
                self.vectorstore = PineconeVectorStore(
                    index_name=index_name,
                    embedding=self.embeddings
                )
            else:
                raise ImportError(
                    "Pinecone package not installed. "
                    "Install with: pip install pinecone"
                )
            
            logger.info(f"Pinecone initialized: {index_name}")
            
        except Exception as e:
            logger.error(f"Failed to initialize Pinecone: {e}")
            raise Exception(f"Pinecone initialization failed: {str(e)}")
    
    def add_documents(
        self,
        documents: List[Document],
        ids: Optional[List[str]] = None
    ) -> List[str]:
        """
        Add documents to vector store.
        
        Args:
            documents: List of Document objects to add
            ids: Optional list of document IDs
            
        Returns:
            List of document IDs that were added
        """
        try:
            if not documents:
                logger.warning("No documents to add")
                return []
            
            logger.info(f"Adding {len(documents)} documents to vector store")
            
            # Add documents
            if ids:
                result = self.vectorstore.add_documents(documents, ids=ids)
            else:
                result = self.vectorstore.add_documents(documents)
            
            # Persist if Chroma
            if self.vector_db_type == "chroma":
                self.vectorstore.persist()
            
            logger.info(f"Successfully added {len(documents)} documents")
            return result if isinstance(result, list) else []
            
        except Exception as e:
            logger.error(f"Failed to add documents: {e}")
            raise Exception(f"Failed to add documents: {str(e)}")
    
    def similarity_search(
        self,
        query: str,
        k: int = 5,
        filter: Optional[dict] = None
    ) -> List[Document]:
        """
        Search for similar documents.
        
        Args:
            query: Search query string
            k: Number of results to return
            filter: Optional metadata filter
            
        Returns:
            List of similar Document objects
        """
        try:
            logger.info(f"Searching vector store: query='{query[:50]}...', k={k}")
            
            if filter:
                results = self.vectorstore.similarity_search(
                    query=query,
                    k=k,
                    filter=filter
                )
            else:
                results = self.vectorstore.similarity_search(query=query, k=k)
            
            logger.info(f"Found {len(results)} similar documents")
            return results
            
        except Exception as e:
            logger.error(f"Similarity search failed: {e}")
            raise Exception(f"Search failed: {str(e)}")
    
    def similarity_search_with_score(
        self,
        query: str,
        k: int = 5,
        filter: Optional[dict] = None
    ) -> List[tuple[Document, float]]:
        """
        Search with similarity scores.
        
        Args:
            query: Search query string
            k: Number of results to return
            filter: Optional metadata filter
            
        Returns:
            List of tuples (Document, score)
        """
        try:
            logger.info(f"Searching with scores: query='{query[:50]}...', k={k}")
            
            if filter:
                results = self.vectorstore.similarity_search_with_score(
                    query=query,
                    k=k,
                    filter=filter
                )
            else:
                results = self.vectorstore.similarity_search_with_score(
                    query=query,
                    k=k
                )
            
            logger.info(f"Found {len(results)} results with scores")
            return results
            
        except Exception as e:
            logger.error(f"Search with scores failed: {e}")
            raise Exception(f"Search failed: {str(e)}")
    
    def as_retriever(
        self,
        k: int = 5,
        search_type: str = "similarity",
        search_kwargs: Optional[dict] = None
    ):
        """
        Get vector store as LangChain retriever.
        
        Args:
            k: Number of documents to retrieve
            search_type: Type of search ("similarity", "mmr", etc.)
            search_kwargs: Additional search parameters
            
        Returns:
            Retriever object
        """
        try:
            kwargs = search_kwargs or {}
            
            retriever = self.vectorstore.as_retriever(
                search_type=search_type,
                search_kwargs={"k": k, **kwargs}
            )
            
            logger.info(f"Retriever created: k={k}, search_type={search_type}")
            return retriever
            
        except Exception as e:
            logger.error(f"Failed to create retriever: {e}")
            raise Exception(f"Retriever creation failed: {str(e)}")
    
    def delete_documents(self, ids: List[str]) -> None:
        """
        Delete documents by IDs.
        
        Args:
            ids: List of document IDs to delete
        """
        try:
            if not ids:
                return
            
            logger.info(f"Deleting {len(ids)} documents")
            
            if self.vector_db_type == "chroma":
                self.vectorstore.delete(ids=ids)
                self.vectorstore.persist()
            elif self.vector_db_type == "pinecone":
                # Pinecone deletion
                self.vectorstore.delete(ids=ids)
            
            logger.info(f"Successfully deleted {len(ids)} documents")
            
        except Exception as e:
            logger.error(f"Failed to delete documents: {e}")
            raise Exception(f"Deletion failed: {str(e)}")
    
    def get_collection_info(self) -> dict:
        """
        Get information about the vector store collection.
        
        Returns:
            Dictionary with collection information
        """
        try:
            info = {
                "type": self.vector_db_type,
                "collection_name": self.collection_name,
                "embedding_model": settings.embedding_model
            }
            
            if self.vector_db_type == "chroma":
                # Get Chroma collection info
                collection = self.vectorstore._collection
                info["count"] = collection.count()
            elif self.vector_db_type == "pinecone":
                # Get Pinecone index info
                if PineconeClient and settings.pinecone_api_key:
                    try:
                        pc = PineconeClient(api_key=settings.pinecone_api_key)
                        index = pc.Index(settings.pinecone_index_name)
                        stats = index.describe_index_stats()
                        info["count"] = stats.get("total_vector_count", 0)
                    except Exception as e:
                        logger.warning(f"Failed to get Pinecone stats: {e}")
                        info["count"] = 0
                elif pinecone:
                    try:
                        index = pinecone.Index(settings.pinecone_index_name)
                        info["count"] = index.describe_index_stats().get("total_vector_count", 0)
                    except Exception as e:
                        logger.warning(f"Failed to get Pinecone stats: {e}")
                        info["count"] = 0
                else:
                    info["count"] = 0
            
            return info
            
        except Exception as e:
            logger.error(f"Failed to get collection info: {e}")
            return {"type": self.vector_db_type, "error": str(e)}


# Global vector store instance
_vector_store: Optional[VectorStore] = None


def get_vector_store(
    collection_name: Optional[str] = None,
    persist_directory: Optional[str] = None
) -> VectorStore:
    """
    Get or create global vector store instance (singleton).
    
    Args:
        collection_name: Collection/index name
        persist_directory: Persistence directory (Chroma only)
        
    Returns:
        VectorStore instance
    """
    global _vector_store
    
    if _vector_store is None:
        _vector_store = VectorStore(
            collection_name=collection_name,
            persist_directory=persist_directory
        )
    
    return _vector_store


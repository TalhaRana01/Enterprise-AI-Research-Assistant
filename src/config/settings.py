"""Application settings and configuration."""

from typing import List, Optional
from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""
    
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
        env_ignore_empty=True
    )
    
    # Environment
    environment: str = Field(default="development", description="Environment name")
    debug: bool = Field(default=False, description="Debug mode")
    
    # API Configuration
    api_host: str = Field(default="0.0.0.0", description="API host")
    api_port: int = Field(default=8000, description="API port")
    api_workers: int = Field(default=1, description="Number of workers")
    
    # OpenAI Configuration
    openai_api_key: str = Field(..., description="OpenAI API key")
    llm_model: str = Field(default="gpt-3.5-turbo", description="LLM model")
    llm_temperature: float = Field(default=0.0, description="LLM temperature")
    llm_max_tokens: int = Field(default=2000, description="Max tokens per request")
    embedding_model: str = Field(
        default="text-embedding-3-small",
        description="Embedding model"
    )
    
    # Vector Database
    vector_db_type: str = Field(default="chroma", description="Vector DB type")
    chroma_persist_directory: str = Field(
        default="./data/chroma",
        description="Chroma persistence directory"
    )
    pinecone_api_key: Optional[str] = Field(default=None, description="Pinecone API key")
    pinecone_environment: Optional[str] = Field(
        default=None,
        description="Pinecone environment"
    )
    pinecone_index_name: Optional[str] = Field(
        default=None,
        description="Pinecone index name"
    )
    
    # Database
    database_url: str = Field(
        default="postgresql://postgres:postgres@localhost:5432/research_assistant_dev",
        description="Database URL"
    )
    database_pool_size: int = Field(default=5, description="DB pool size")
    database_max_overflow: int = Field(default=10, description="DB max overflow")
    
    # Redis
    redis_url: str = Field(
        default="redis://localhost:6379/0",
        description="Redis URL"
    )
    redis_max_connections: int = Field(
        default=10,
        description="Redis max connections"
    )
    
    # Caching
    enable_llm_cache: bool = Field(default=True, description="Enable LLM caching")
    cache_ttl: int = Field(default=3600, description="Cache TTL in seconds")
    
    # Rate Limiting
    rate_limit_enabled: bool = Field(default=True, description="Enable rate limiting")
    rate_limit_per_minute: int = Field(
        default=60,
        description="Requests per minute"
    )
    
    # Monitoring
    langchain_tracing_v2: bool = Field(
        default=False,
        description="Enable LangSmith tracing"
    )
    langchain_project: str = Field(
        default="ai-research-assistant",
        description="LangSmith project name"
    )
    langchain_api_key: Optional[str] = Field(
        default=None,
        description="LangSmith API key"
    )
    langchain_endpoint: str = Field(
        default="https://api.smith.langchain.com",
        description="LangSmith endpoint"
    )
    
    # Logging
    log_level: str = Field(default="INFO", description="Log level")
    log_format: str = Field(default="json", description="Log format")
    log_file: str = Field(default="logs/app.log", description="Log file path")
    
    # Security
    secret_key: str = Field(..., description="Secret key for JWT")
    jwt_algorithm: str = Field(default="HS256", description="JWT algorithm")
    access_token_expire_minutes: int = Field(
        default=30,
        description="Access token expiration"
    )
    
    # CORS
    cors_origins: List[str] = Field(
        default=["http://localhost:3000"],
        description="CORS origins"
    )
    
    # External APIs
    arxiv_max_results: int = Field(default=10, description="ArXiv max results")
    pubmed_api_key: Optional[str] = Field(default=None, description="PubMed API key")
    semantic_scholar_api_key: Optional[str] = Field(
        default=None,
        description="Semantic Scholar API key"
    )
    
    # Feature Flags
    enable_multi_source_search: bool = Field(
        default=True,
        description="Enable multi-source search"
    )
    enable_citation_generation: bool = Field(
        default=True,
        description="Enable citation generation"
    )
    enable_advanced_summarization: bool = Field(
        default=True,
        description="Enable advanced summarization"
    )
    
    # Cost Management
    max_tokens_per_request: int = Field(
        default=4000,
        description="Max tokens per request"
    )
    max_tokens_per_user_per_day: int = Field(
        default=50000,
        description="Max tokens per user per day"
    )
    cost_alert_threshold: float = Field(
        default=10.0,
        description="Cost alert threshold in USD"
    )
    
    # Performance
    request_timeout: int = Field(default=30, description="Request timeout in seconds")
    max_concurrent_requests: int = Field(
        default=10,
        description="Max concurrent requests"
    )
    chunk_size: int = Field(default=1000, description="Text chunk size")
    chunk_overlap: int = Field(default=200, description="Text chunk overlap")
    
    # Development
    enable_api_docs: bool = Field(default=True, description="Enable API docs")
    enable_profiling: bool = Field(default=False, description="Enable profiling")
    mock_external_apis: bool = Field(default=False, description="Mock external APIs")
    
    @property
    def is_production(self) -> bool:
        """Check if running in production."""
        return self.environment == "production"
    
    @property
    def is_development(self) -> bool:
        """Check if running in development."""
        return self.environment == "development"


# Global settings instance
settings = Settings()


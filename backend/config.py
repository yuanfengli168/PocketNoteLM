from functools import lru_cache
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

    # LLM provider: "openai" or "ollama"
    llm_provider: str = "openai"

    # OpenAI
    openai_api_key: str = ""
    openai_model: str = "gpt-4o"
    openai_embedding_model: str = "text-embedding-3-small"

    # Ollama
    ollama_base_url: str = "http://localhost:11434"
    ## ollama model qwen3:14b works, and is very fast.
    #ollama_model: str = "qwen3:14b"
    # change to qwen3:32b for better embeddings if you have the resources (needs pull of ~20GB)
    ollama_model: str = "qwen3:32b"
    ollama_embedding_model: str = "nomic-embed-text"

    # Docs
    docs_folder_path: str = "./docs"

    # Admin
    admin_token: str = "change-me"

    # Server
    host: str = "0.0.0.0"
    port: int = 8000

    # ChromaDB
    chroma_persist_dir: str = "./chroma_db"

    # Database
    database_url: str = "sqlite:///./pocketnotelm.db"

    # Cache
    cache_ttl: int = 300


@lru_cache
def get_settings() -> Settings:
    return Settings()

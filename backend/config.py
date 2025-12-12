from pydantic_settings import BaseSettings
from pydantic import Field

class Settings(BaseSettings):
    groq_api_key: str = Field("", env="GROQ_API_KEY")   # ✅ NEW
    embedding_model: str = Field("all-MiniLM-L6-v2", env="EMBEDDING_MODEL")  # Local embedding model (sentence-transformers)
    llm_model: str = Field("llama-3.1-8b-instant", env="LLM_MODEL")  # ⭐ Recommended Groq model
    top_k: int = Field(4, env="TOP_K")
    chunk_size: int = Field(500, env="CHUNK_SIZE")
    chunk_overlap: int = Field(80, env="CHUNK_OVERLAP")
    data_dir: str = Field("data", env="DATA_DIR")
    embeddings_dir: str = Field("embeddings", env="EMBEDDINGS_DIR")
    index_file: str = Field("embeddings/index.faiss", env="INDEX_FILE")
    metadata_file: str = Field("embeddings/meta.json", env="METADATA_FILE")
    backend_host: str = Field("0.0.0.0", env="BACKEND_HOST")
    backend_port: int = Field(8000, env="BACKEND_PORT")
    BACKEND_URL: str = Field(default="http://localhost:8000")

    class Config:
        env_file = ".env"


settings = Settings()

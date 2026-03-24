from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    SERVICE_NAME: str = "OCR Document Processing NLP Service"
    SERVICE_VERSION: str = "1.0.0"
    SERVICE_PORT: int = 8001
    SPACY_MODEL: str = "en_core_web_sm"
    EMBEDDING_MODEL: str = "all-MiniLM-L6-v2"
    OLLAMA_MODEL: str = "llama3.2"
    OLLAMA_BASE_URL: str = "http://localhost:11434"
    TOP_K: int = 5

    class Config:
        env_file = ".env"


settings = Settings()

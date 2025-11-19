"""
Configuration management for NEXXBot
Handles environment variables and system settings
"""

import os
from pathlib import Path
from typing import Optional
from pydantic_settings import BaseSettings
from pydantic import Field


class Settings(BaseSettings):
    """Application settings"""

    # Project paths
    BASE_DIR: Path = Path(__file__).parent.parent.parent
    DATA_DIR: Path = BASE_DIR / "data"
    LOG_DIR: Path = BASE_DIR / "logs"
    MODEL_DIR: Path = BASE_DIR / "models"

    # OpenAI Configuration
    OPENAI_API_KEY: str = Field(default="", env="OPENAI_API_KEY")
    OPENAI_MODEL: str = Field(default="gpt-4-turbo-preview", env="OPENAI_MODEL")
    OPENAI_TEMPERATURE: float = Field(default=0.7, env="OPENAI_TEMPERATURE")
    OPENAI_MAX_TOKENS: int = Field(default=4000, env="OPENAI_MAX_TOKENS")

    # Anthropic Configuration
    ANTHROPIC_API_KEY: Optional[str] = Field(default=None, env="ANTHROPIC_API_KEY")

    # Vector Database
    VECTOR_DB_TYPE: str = Field(default="chromadb", env="VECTOR_DB_TYPE")
    PINECONE_API_KEY: Optional[str] = Field(default=None, env="PINECONE_API_KEY")
    PINECONE_ENVIRONMENT: str = Field(default="gcp-starter", env="PINECONE_ENVIRONMENT")

    # Database
    DATABASE_URL: str = Field(
        default="postgresql://user:password@localhost:5432/nexxbot",
        env="DATABASE_URL"
    )
    REDIS_URL: str = Field(default="redis://localhost:6379/0", env="REDIS_URL")

    # API Configuration
    API_HOST: str = Field(default="0.0.0.0", env="API_HOST")
    API_PORT: int = Field(default=8000, env="API_PORT")
    API_DEBUG: bool = Field(default=True, env="API_DEBUG")

    # Security
    SECRET_KEY: str = Field(
        default="your-secret-key-change-in-production",
        env="SECRET_KEY"
    )
    ALGORITHM: str = Field(default="HS256", env="ALGORITHM")
    ACCESS_TOKEN_EXPIRE_MINUTES: int = Field(default=30, env="ACCESS_TOKEN_EXPIRE_MINUTES")

    # Agent Configuration
    MAX_AGENT_ITERATIONS: int = Field(default=10, env="MAX_AGENT_ITERATIONS")
    AGENT_TIMEOUT: int = Field(default=300, env="AGENT_TIMEOUT")

    # Logging
    LOG_LEVEL: str = Field(default="INFO", env="LOG_LEVEL")
    LOG_FILE: str = Field(default="logs/nexxbot.log", env="LOG_FILE")

    # Feature Flags
    ENABLE_EMBODIED_AI: bool = Field(default=False, env="ENABLE_EMBODIED_AI")
    ENABLE_VISION_QC: bool = Field(default=True, env="ENABLE_VISION_QC")
    ENABLE_SALES_AGENT: bool = Field(default=True, env="ENABLE_SALES_AGENT")

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = True

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        # Create necessary directories
        self.LOG_DIR.mkdir(parents=True, exist_ok=True)
        self.DATA_DIR.mkdir(parents=True, exist_ok=True)
        self.MODEL_DIR.mkdir(parents=True, exist_ok=True)


# Global settings instance
settings = Settings()

from pydantic_settings import BaseSettings, SettingsConfigDict
from typing import Optional
from pydantic import Field, field_validator


class Settings(BaseSettings):
    """
    Runtime settings.

    NOTE: Business rules / thresholds are NOT placed here.
    Those live in MongoDB collections and are fully user-configurable.
    """

    # Service
    SERVICE_NAME: str = "upwork-proposal-bot"
    LOG_LEVEL: str = "INFO"

    # Mongo - Required fields, validated at startup
    MONGODB_URI: str = Field(
        ...,
        description="MongoDB connection URI (e.g., mongodb://localhost:27017). Database name should NOT be included.",
        examples=["mongodb://localhost:27017"]
    )
    MONGODB_DB: str = Field(
        ...,
        description="MongoDB database name (e.g., upwork_proposal_bot)",
        examples=["upwork_proposal_bot"]
    )

    # OpenAI
    OPENAI_API_KEY: Optional[str] = None

    # n8n ingestion security (optional, but recommended)
    N8N_SHARED_SECRET: Optional[str] = None
    
    # Vollna Bearer Token (for webhook authentication)
    VOLLNA_BEARER_TOKEN: Optional[str] = Field(
        None,
        description="Bearer token for Vollna webhook authentication. If not set, uses N8N_SHARED_SECRET as fallback."
    )
    
    # CORS configuration
    CORS_ORIGINS: Optional[str] = Field(
        default="http://localhost:8080,http://localhost:8081,http://localhost:3000,http://localhost:5173,http://127.0.0.1:8080,http://127.0.0.1:8081",
        description="Comma-separated list of allowed CORS origins"
    )

    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    @field_validator("MONGODB_URI")
    @classmethod
    def validate_mongodb_uri(cls, v: str) -> str:
        """Validate MongoDB URI format."""
        if not v:
            raise ValueError("MONGODB_URI cannot be empty")
        if "/" in v.split("://")[-1].split("?")[0]:
            # Check if database name is embedded (common mistake)
            raise ValueError(
                "MONGODB_URI should not include database name. "
                "Use MONGODB_URI=mongodb://localhost:27017 and set MONGODB_DB separately."
            )
        return v

    @field_validator("MONGODB_DB")
    @classmethod
    def validate_mongodb_db(cls, v: str) -> str:
        """Validate MongoDB database name."""
        if not v:
            raise ValueError("MONGODB_DB cannot be empty")
        if not v.replace("_", "").replace("-", "").isalnum():
            raise ValueError("MONGODB_DB must contain only alphanumeric characters, underscores, or hyphens")
        return v


settings = Settings()



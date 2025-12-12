from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    DATABASE_URL: str = "mysql+aiomysql://root:@localhost/upwork_db"
    MONGODB_URL: str = "mongodb://localhost:27017/upwork"

    model_config = SettingsConfigDict(
        env_file=".env",
        extra="ignore"
    )


settings = Settings()

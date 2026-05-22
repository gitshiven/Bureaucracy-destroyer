from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    DATABASE_URL: str
    ANTHROPIC_API_KEY: str
    OPENAI_API_KEY: str
    USE_TEXTRACT: bool = False
    AWS_ACCESS_KEY_ID: str = ""
    AWS_SECRET_ACCESS_KEY: str = ""
    AWS_REGION: str = "eu-west-1"
    PGVECTOR_ENABLED: bool = True
    ENVIRONMENT: str = "development"
    SECRET_KEY: str = "change-me"

    class Config:
        env_file = ".env"
        extra = "ignore"

settings = Settings()
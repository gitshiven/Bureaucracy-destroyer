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
    TWILIO_ACCOUNT_SID="AC854a7c1d2d46866d21772ae45aa546cf"
    TWILIO_AUTH_TOKEN="0ad1a5aba5c8209f998d8e18e8610842"
    TWILIO_WHATSAPP_FROM="whatsapp:+14155238886"

    class Config:
        env_file = ".env"
        extra = "ignore"

settings = Settings()
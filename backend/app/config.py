from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    DATABASE_URL: str = "sqlite:///./gaint_academy.db"
    SECRET_KEY: str = "change-this-in-production"
    ACCESS_TOKEN_EXPIRE_HOURS: int = 8
    CORS_ORIGINS: str = "http://localhost:5173,http://127.0.0.1:5173"
    ALGORITHM: str = "HS256"

settings = Settings()

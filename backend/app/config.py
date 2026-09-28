from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    DATABASE_URL: str = "sqlite:///./gaint_academy.db"
    SECRET_KEY: str = "change-this-in-production"
    ACCESS_TOKEN_EXPIRE_HOURS: int = 8
    CORS_ORIGINS: str = "http://localhost:5173,http://127.0.0.1:5173"
    ALGORITHM: str = "HS256"
    APP_ENV: str = "development"
    AUTO_CREATE_SCHEMA: bool = True
    SEED_DEMO_DATA: bool = True

    @property
    def is_production(self) -> bool:
        return self.APP_ENV.strip().lower() == "production"

    def validate_runtime(self) -> None:
        if self.is_production and self.AUTO_CREATE_SCHEMA:
            raise RuntimeError("AUTO_CREATE_SCHEMA must be false in production; run Alembic migrations before startup")
        if self.is_production and self.SEED_DEMO_DATA:
            raise RuntimeError("SEED_DEMO_DATA must be false in production")
        if self.is_production and self.SECRET_KEY == "change-this-in-production":
            raise RuntimeError("SECRET_KEY must be configured in production")

settings = Settings()

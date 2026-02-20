import os

from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """애플리케이션 설정"""

    # 환경
    ENVIRONMENT: str = "development"
    DEBUG: bool = True

    # 서버
    HOST: str = "0.0.0.0"
    PORT: int = 6300

    # 데이터베이스
    DATABASE_URL: str = "sqlite:///./bitcoin_news.db"

    # 보안
    SECRET_KEY: str = "dev-secret-key-change-in-production"
    OPENAI_API_KEY: str = ""
    TRANSLATION_REQUIRED: bool = True

    # CORS
    CORS_ORIGINS: list[str] = ["http://localhost:6200", "http://localhost:5173"]

    class Config:
        env_file = ".env"
        extra = "allow"


settings = Settings()

# 프로덕션 환경에서 DEBUG 비활성화
if settings.ENVIRONMENT == "production":
    settings.DEBUG = False

# Railway 환경에서 PORT 환경변수 사용
if os.getenv("PORT"):
    settings.PORT = int(os.getenv("PORT"))

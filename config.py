from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    XATA_API_KEY: str
    XATA_BASE_URL: str

    class Config:
        env_file = ".env"

settings = Settings()

from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    SUPABASE_URL: str = ""
    SUPABASE_KEY: str = ""
    OPENWEATHER_API_KEY: str = ""
    GOOGLE_MAPS_API_KEY: str = ""
    DEBUG: bool = True
    ALLOWED_ORIGINS: str = "http://localhost:5500,http://127.0.0.1:5500"
    
    class Config:
        env_file = ".env"

settings = Settings()
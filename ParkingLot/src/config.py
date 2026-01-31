"""Application configuration."""
from pydantic_settings import BaseSettings
from functools import lru_cache


class Settings(BaseSettings):
    """Application settings from environment variables."""
    
    # Database
    database_url: str = "postgresql://postgres:password@localhost:5432/parking_lot_db"
    
    # API
    api_host: str = "0.0.0.0"
    api_port: int = 8000
    api_reload: bool = True
    
    # Security
    secret_key: str = "your-secret-key-change-in-production"
    
    # Redis (optional)
    redis_url: str = "redis://localhost:6379/0"
    
    # Application
    debug: bool = True
    log_level: str = "INFO"
    
    # Pricing
    base_hourly_rate: float = 5.0
    dynamic_pricing_enabled: bool = True
    dynamic_pricing_threshold: float = 0.9
    dynamic_pricing_multiplier: float = 1.5
    
    class Config:
        """Pydantic configuration."""
        env_file = ".env"
        case_sensitive = False


@lru_cache()
def get_settings() -> Settings:
    """Get cached settings instance.
    
    Returns:
        Settings instance
    """
    return Settings()

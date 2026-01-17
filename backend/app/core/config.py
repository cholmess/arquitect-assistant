from pydantic_settings import BaseSettings
from typing import Optional

class Settings(BaseSettings):
    app_name: str = "Arquitect Assistant"
    debug: bool = True
    version: str = "1.0.0"
    
    # Database
    database_url: str = "sqlite:///./arquitect_assistant.db"
    
    # File upload
    max_file_size: int = 10 * 1024 * 1024  # 10MB
    allowed_extensions: list = [".pdf", ".jpg", ".jpeg", ".png"]
    
    # OGUC Settings
    min_surface_area: float = 40.0  # m² mínimos para vivienda
    default_max_height: float = 23.0  # metros por defecto
    default_constructibility_coef: float = 1.0  # coeficiente por defecto
    
    # OCR Settings
    tesseract_cmd: Optional[str] = None
    
    class Config:
        env_file = ".env"

settings = Settings()

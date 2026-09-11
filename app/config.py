import os

class Settings:
    PROJECT_NAME: str = "RoboCode Challenge"
    SECRET_KEY: str = os.getenv("SECRET_KEY", "super_secret_jwt_key_robocode_2026_gamified")
    ALGORITHM: str = os.getenv("ALGORITHM", "HS256")
    ACCESS_TOKEN_EXPIRE_MINUTES: int = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "1440"))
    
    # Database URL configuration
    DATABASE_URL: str = os.getenv("DATABASE_URL", "postgresql://robocode:robocode_secret_pass@localhost:5432/robocode_db")

settings = Settings()

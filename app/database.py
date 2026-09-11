import os
import logging
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base

logger = logging.getLogger("robocode")

DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://robocode:robocode_secret_pass@localhost:5432/robocode_db")

engine = None
try:
    if DATABASE_URL.startswith("sqlite"):
        engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
    else:
        # Tenta conectar ao PostgreSQL
        engine = create_engine(DATABASE_URL, pool_pre_ping=True)
        # Test connection
        with engine.connect() as conn:
            pass
        print(f"[OK] Conectado com sucesso ao PostgreSQL: {DATABASE_URL}")
except Exception as e:
    print(f"[AVISO] Nao foi possivel conectar ao PostgreSQL ({e}).")
    print("[INFO] Alternando automaticamente para SQLite local ('sqlite:///./robocode.db') para execucao imediata!")
    DATABASE_URL = "sqlite:///./robocode.db"
    engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

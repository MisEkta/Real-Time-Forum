from sqlalchemy.engine import create_engine
from sqlalchemy.orm import sessionmaker
from .models import Base
from sqlalchemy.pool import QueuePool

DATABASE_URL = "postgresql://username:password@localhost/postgres"

# Configure engine with custom pool settings
engine = create_engine(
    DATABASE_URL,
    echo=False,
    poolclass=QueuePool,
    pool_size=20,  # Increase pool size
    max_overflow=30,  # Increase max overflow
    pool_timeout=60,  # Increase timeout
    pool_pre_ping=True  # Enable connection health checks
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def init_db():
    Base.metadata.create_all(bind=engine)
    print("Database initialized")
    return engine

def get_db():
    db = SessionLocal()
    try:
        return db
    finally:
        db.close()
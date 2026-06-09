"""
Database connection and session management.
"""
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.pool import QueuePool
from typing import Generator
import logging

from config import settings
from database.models import Base

logger = logging.getLogger(__name__)

# Create engine based on configuration
if settings.USE_SQLITE:
    # SQLite for development - handle Windows paths
    db_path = settings.SQLITE_DB_PATH.replace("\\", "/")
    engine = create_engine(
        f"sqlite:///{db_path}",
        connect_args={"check_same_thread": False},
        echo=settings.DATABASE_ECHO,
    )
    logger.info(f"SQLite database: {db_path}")
else:
    # PostgreSQL for production
    engine = create_engine(
        settings.DATABASE_URL,
        poolclass=QueuePool,
        pool_size=10,
        max_overflow=20,
        echo=settings.DATABASE_ECHO,
        connect_args={
            "connect_timeout": 10,
        }
    )

# Session factory
SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine,
    expire_on_commit=False
)


def get_db() -> Generator[Session, None, None]:
    """
    Dependency for FastAPI to get database session.
    Usage: @app.get("/") def read_root(db: Session = Depends(get_db))
    """
    db = SessionLocal()
    try:
        yield db
    except Exception as e:
        logger.error(f"Database session error: {str(e)}")
        db.rollback()
        raise
    finally:
        db.close()


def init_db():
    """Initialize database tables."""
    try:
        Base.metadata.create_all(bind=engine)
        logger.info("Database initialized successfully")
    except Exception as e:
        logger.error(f"Failed to initialize database: {str(e)}")
        raise


def drop_db():
    """Drop all database tables (for testing)."""
    try:
        Base.metadata.drop_all(bind=engine)
        logger.info("Database dropped successfully")
    except Exception as e:
        logger.error(f"Failed to drop database: {str(e)}")
        raise


def health_check() -> bool:
    """Check database connection health."""
    try:
        with engine.connect() as conn:
            conn.execute(text("SELECT 1"))
        return True
    except Exception as e:
        logger.error(f"Database health check failed: {str(e)}")
        return False

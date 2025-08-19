"""
Database session management and utilities.
"""

from typing import Generator, Optional
from sqlalchemy import create_engine, Engine
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.pool import StaticPool
from loguru import logger

from .config import settings
from ..models.database import Base


class DatabaseManager:
    """Database manager for handling connections and sessions."""
    
    def __init__(self, database_url: Optional[str] = None):
        """Initialize database manager with connection URL."""
        self.database_url = database_url or settings.DATABASE_URL
        self.engine: Optional[Engine] = None
        self.SessionLocal: Optional[sessionmaker] = None
        
    def initialize(self) -> None:
        """Initialize database engine and session factory."""
        logger.info(f"Initializing database connection to: {self._safe_url()}")
        
        # Configure engine based on database type
        if self.database_url.startswith("sqlite"):
            # SQLite configuration
            self.engine = create_engine(
                self.database_url,
                connect_args={"check_same_thread": False},
                poolclass=StaticPool,
                echo=settings.DEBUG,
            )
        else:
            # PostgreSQL or other database configuration
            self.engine = create_engine(
                self.database_url,
                pool_pre_ping=True,
                pool_recycle=300,
                echo=settings.DEBUG,
            )
        
        # Create session factory
        self.SessionLocal = sessionmaker(
            autocommit=False,
            autoflush=False,
            bind=self.engine,
        )
        
        logger.info("Database connection initialized successfully")
    
    def create_tables(self) -> None:
        """Create all database tables."""
        if not self.engine:
            raise RuntimeError("Database not initialized. Call initialize() first.")
        
        logger.info("Creating database tables...")
        Base.metadata.create_all(bind=self.engine)
        logger.info("Database tables created successfully")
    
    def drop_tables(self) -> None:
        """Drop all database tables."""
        if not self.engine:
            raise RuntimeError("Database not initialized. Call initialize() first.")
        
        logger.warning("Dropping all database tables...")
        Base.metadata.drop_all(bind=self.engine)
        logger.warning("All database tables dropped")
    
    def get_session(self) -> Generator[Session, None, None]:
        """Get database session with automatic cleanup."""
        if not self.SessionLocal:
            raise RuntimeError("Database not initialized. Call initialize() first.")
        
        session = self.SessionLocal()
        try:
            yield session
        except Exception as e:
            logger.error(f"Database session error: {e}")
            session.rollback()
            raise
        finally:
            session.close()
    
    def health_check(self) -> bool:
        """Check database connectivity."""
        try:
            if not self.engine:
                return False

            from sqlalchemy import text
            with self.engine.connect() as connection:
                connection.execute(text("SELECT 1"))
            return True
        except Exception as e:
            logger.error(f"Database health check failed: {e}")
            return False
    
    def _safe_url(self) -> str:
        """Get database URL with password masked for logging."""
        url = self.database_url
        if "://" in url and "@" in url:
            # Mask password in URL for logging
            parts = url.split("://")
            if len(parts) == 2:
                scheme = parts[0]
                rest = parts[1]
                if "@" in rest:
                    auth_part, host_part = rest.split("@", 1)
                    if ":" in auth_part:
                        user, _ = auth_part.split(":", 1)
                        return f"{scheme}://{user}:***@{host_part}"
        return url


# Global database manager instance
db_manager = DatabaseManager()


def get_database_session() -> Generator[Session, None, None]:
    """Dependency function for FastAPI to get database session."""
    yield from db_manager.get_session()


def init_database() -> None:
    """Initialize database connection and create tables."""
    db_manager.initialize()
    db_manager.create_tables()


def close_database() -> None:
    """Close database connections."""
    if db_manager.engine:
        db_manager.engine.dispose()
        logger.info("Database connections closed")


# Database utilities
class DatabaseUtils:
    """Utility functions for database operations."""
    
    @staticmethod
    def reset_database() -> None:
        """Reset database by dropping and recreating all tables."""
        logger.warning("Resetting database - all data will be lost!")
        db_manager.drop_tables()
        db_manager.create_tables()
        logger.info("Database reset completed")
    
    @staticmethod
    def check_connection() -> bool:
        """Check if database connection is healthy."""
        return db_manager.health_check()
    
    @staticmethod
    def get_table_info() -> dict:
        """Get information about database tables."""
        if not db_manager.engine:
            return {"error": "Database not initialized"}
        
        try:
            from sqlalchemy import inspect
            inspector = inspect(db_manager.engine)
            tables = inspector.get_table_names()
            
            table_info = {}
            for table in tables:
                columns = inspector.get_columns(table)
                indexes = inspector.get_indexes(table)
                table_info[table] = {
                    "columns": [col["name"] for col in columns],
                    "indexes": [idx["name"] for idx in indexes],
                }
            
            return {
                "tables": table_info,
                "total_tables": len(tables),
            }
        except Exception as e:
            logger.error(f"Error getting table info: {e}")
            return {"error": str(e)}


# Export commonly used items
__all__ = [
    "DatabaseManager",
    "db_manager",
    "get_database_session",
    "init_database",
    "close_database",
    "DatabaseUtils",
]

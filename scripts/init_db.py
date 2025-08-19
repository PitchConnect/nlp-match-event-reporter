#!/usr/bin/env python3
"""
Database initialization script for NLP Match Event Reporter.
"""

import sys
import os
from pathlib import Path

# Add src to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root / "src"))

from nlp_match_event_reporter.core.database import init_database, DatabaseUtils
from nlp_match_event_reporter.core.config import settings
from loguru import logger


def main():
    """Initialize the database with tables and sample data."""
    logger.info("Starting database initialization...")
    logger.info(f"Database URL: {settings.DATABASE_URL}")
    
    try:
        # Initialize database connection and create tables
        init_database()
        logger.info("✅ Database tables created successfully")
        
        # Check connection
        if DatabaseUtils.check_connection():
            logger.info("✅ Database connection verified")
        else:
            logger.error("❌ Database connection failed")
            return 1
        
        # Get table information
        table_info = DatabaseUtils.get_table_info()
        if "error" not in table_info:
            logger.info(f"✅ Created {table_info['total_tables']} tables:")
            for table_name, info in table_info["tables"].items():
                logger.info(f"  - {table_name}: {len(info['columns'])} columns, {len(info['indexes'])} indexes")
        else:
            logger.error(f"❌ Error getting table info: {table_info['error']}")
        
        logger.info("🎉 Database initialization completed successfully!")
        return 0
        
    except Exception as e:
        logger.error(f"❌ Database initialization failed: {e}")
        return 1


if __name__ == "__main__":
    exit(main())

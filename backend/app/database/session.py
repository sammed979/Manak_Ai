from sqlalchemy import create_engine, event
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from app.config.settings import settings
import logging

logger = logging.getLogger(__name__)

# Use SQLite for local development, PostgreSQL for Docker
if settings.USE_DOCKER_DB:
    DATABASE_URL = settings.DATABASE_URL
    engine = create_engine(DATABASE_URL, echo=settings.DEBUG, pool_pre_ping=True)
else:
    DATABASE_URL = "sqlite:///./manak_ai.db"
    engine = create_engine(
        DATABASE_URL,
        echo=settings.DEBUG,
        connect_args={"check_same_thread": False},
    )


@event.listens_for(engine, "connect")
def _set_sqlite_pragma(dbapi_connection, connection_record):
    if DATABASE_URL.startswith("sqlite"):
        try:
            cursor = dbapi_connection.cursor()
            cursor.execute("PRAGMA foreign_keys=ON;")
            cursor.close()
        except Exception:
            logger.debug("Could not enable foreign_keys pragma", exc_info=True)


SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

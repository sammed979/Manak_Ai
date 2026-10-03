from sqlalchemy import create_engine, event
from sqlalchemy.exc import OperationalError
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from app.config.settings import settings
import logging
import os

logger = logging.getLogger(__name__)

DATABASE_URL: str = "sqlite:///./manak_ai.db"
_engine_configured = False


def _resolve_database_url() -> str:
    """Decide which database URL to actually use.

    Decision order (most specific wins):
      1. If USE_DOCKER_DB is truthy AND settings.DATABASE_URL is set to a
         non-default value (real postgres connection string) -> use PostgreSQL.
      2. Otherwise -> always fall back to SQLite at ./manak_ai.db in the
         current working directory (inside the Docker container or locally).

    This prevents the classic failure: 'Render env vars not yet pasted, user
    deployed anyway, backend tries localhost:5432 -> psycopg2 Connection refused'
    and instead gives you a fully working ephemeral SQLite-based backend that
    survives until env vars are configured.
    """
    default_pg = "postgresql://postgres:postgres@localhost:5432/manak_ai"
    configured_url = (settings.DATABASE_URL or "").strip()
    if settings.USE_DOCKER_DB and configured_url and configured_url != default_pg:
        return configured_url
    if configured_url and configured_url.startswith("sqlite"):
        return configured_url
    if settings.USE_DOCKER_DB:
        logger.warning(
            "USE_DOCKER_DB=true but DATABASE_URL is still the default "
            "'%s' or empty; using SQLite fallback so the backend still boots.",
            configured_url or "<empty>",
        )
    return "sqlite:///./manak_ai.db"


def _build_engine(url: str):
    if url.startswith("sqlite"):
        return create_engine(
            url,
            echo=settings.DEBUG,
            connect_args={"check_same_thread": False, "timeout": 30},
        )
    return create_engine(url, echo=settings.DEBUG, pool_pre_ping=True, pool_timeout=30)


DATABASE_URL = _resolve_database_url()
engine = _build_engine(DATABASE_URL)

if DATABASE_URL.startswith("sqlite"):
    logger.info("Database configured: SQLite (%s)", os.path.abspath("./manak_ai.db"))
else:
    from urllib.parse import urlparse

    try:
        parsed = urlparse(DATABASE_URL)
        logger.info(
            "Database configured: %s://%s:%s%s (user=%s)",
            parsed.scheme or "postgresql",
            parsed.hostname or "<host>",
            parsed.port or "<default port>",
            parsed.path or "/",
            parsed.username or "<none>",
        )
    except Exception:
        logger.info("Database configured: remote connection")


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

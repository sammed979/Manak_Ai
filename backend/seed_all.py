"""
Idempotent seeder for the entire MANAK AI demo dataset.

Order matters:
1. Standards (no FKs)
2. Standard clauses, requirements, tests, test methods, certification schemes (FK → standards)
3. Laboratories, HallmarkingCentres (no FKs)
4. Knowledge documents & chunks (ingestion creates chunks + embeddings)
5. Demo admin user if absent.
"""
from __future__ import annotations

import asyncio
import logging
import sys
from pathlib import Path

# Ensure seed can find app when run as `python seed_all.py`
BACKEND_DIR = Path(__file__).resolve().parent
if str(BACKEND_DIR) not in sys.path:
    sys.path.insert(0, str(BACKEND_DIR))

from app.database.session import SessionLocal  # noqa: E402
from app.security.auth import get_password_hash  # noqa: E402
from app.models.user import User, UserRole  # noqa: E402

logging.basicConfig(level=logging.INFO, format="[%(levelname)s] %(message)s")
logger = logging.getLogger("seed_all")


def _seed_admin_user() -> None:
    """Create a default admin user if not present.

    Credentials: admin@manak.ai / Admin@123456
    Marked as demo — clear for any real deployment.
    """
    db = SessionLocal()
    try:
        email = "admin@manak.ai"
        existing = db.query(User).filter(User.email == email).first()
        if existing:
            logger.info("Admin user already exists; skipping creation.")
            return
        admin = User(
            email=email,
            full_name="Manak AI Administrator (DEMO)",
            password_hash=get_password_hash("Admin@123456"),
            role=UserRole.ADMIN,
            is_active=True,
        )
        db.add(admin)
        db.commit()
        logger.info("Created demo admin user: admin@manak.ai / Admin@123456")
    except Exception:
        logger.exception("Failed to seed admin user")
        db.rollback()
    finally:
        db.close()


def seed_standards() -> None:
    import seed_standards  # type: ignore[import-not-found]

    seed_standards.seed_standards()


def seed_clauses_requirements_tests_schemes() -> None:
    try:
        import seed_clauses_requirements  # type: ignore[import-not-found]

        seed_clauses_requirements.seed_clauses_requirements()
    except ImportError:
        logger.warning(
            "seed_clauses_requirements.py not yet available; skipping clauses/tests seeding."
        )


def seed_labs_and_hallmarks() -> None:
    try:
        import seed_labs  # type: ignore[import-not-found]

        seed_labs.seed_labs()
    except ImportError:
        logger.warning("seed_labs.py not yet available; skipping labs/hallmarks seeding.")


def seed_knowledge() -> None:
    import seed_knowledge_base  # type: ignore[import-not-found]

    asyncio.run(seed_knowledge_base.seed_knowledge_base())


def main() -> int:
    logger.info("Initializing database tables...")
    import init_db  # type: ignore[import-not-found]

    init_db.init_db()

    logger.info("1/5 Seeding standards metadata...")
    seed_standards()

    logger.info("2/5 Seeding clauses, requirements, tests, certification schemes...")
    seed_clauses_requirements_tests_schemes()

    logger.info("3/5 Seeding laboratories & hallmarking centres...")
    seed_labs_and_hallmarks()

    logger.info("4/5 Seeding knowledge documents (RAG corpus)...")
    seed_knowledge()


    logger.info("5/5 Ensuring demo admin user...")
    _seed_admin_user()

    logger.info("✅ Seed complete. Data is clearly marked as DEMO.")
    logger.info("   Default admin (demo): admin@manak.ai / Admin@123456")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

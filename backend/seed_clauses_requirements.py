"""
Seed standard clauses, requirements, tests, and certification schemes.
Links to standards seeded by seed_standards.py.
"""
from __future__ import annotations

import logging
import sys
from pathlib import Path

BACKEND_DIR = Path(__file__).resolve().parent
if str(BACKEND_DIR) not in sys.path:
    sys.path.insert(0, str(BACKEND_DIR))

from app.database.session import SessionLocal
from app.models.standard import (
    Standard, StandardClause, Requirement, Test, CertificationScheme
)

logging.basicConfig(level=logging.INFO, format="[%(levelname)s] %(message)s")
logger = logging.getLogger("seed_clauses")


def seed_clauses_requirements() -> None:
    db = SessionLocal()
    try:
        existing = db.query(StandardClause).count()
        if existing > 0:
            logger.info("Clauses already seeded (%d records); skipping.", existing)
            return

        # Fetch standards by number
        def get_std(number: str):
            return db.query(Standard).filter(Standard.standard_number == number).first()

        # IS 17342 — Water Bottles
        std = get_std("IS 17342:2020")
        if std:
            clauses = [
                StandardClause(standard_id=std.id, clause_number="4", title="Materials",
                               content="Food-grade stainless steel conforming to IS 6911 or equivalent."),
                StandardClause(standard_id=std.id, clause_number="5", title="Design Requirements",
                               content="Leak-proof cap, smooth inner surface, easy to clean."),
                StandardClause(standard_id=std.id, clause_number="6", title="Performance Requirements",
                               content="Leak test, thermal insulation test, drop test from 1 metre."),
                StandardClause(standard_id=std.id, clause_number="7", title="Marking",
                               content="Manufacturer name, capacity, material grade, country of origin."),
            ]
            for c in clauses:
                db.add(c)
            db.flush()
            req = Requirement(standard_id=std.id, clause_id=clauses[2].id,
                              requirement_number="6.1",
                              description="No leakage when filled with water and inverted for 30 minutes.",
                              category="Performance")
            db.add(req)

        # IS 302-1 — Electrical Appliances
        std = get_std("IS 302-1:2021")
        if std:
            clauses = [
                StandardClause(standard_id=std.id, clause_number="7", title="Marking and Instructions",
                               content="Rated voltage, rated power, manufacturer name, model number."),
                StandardClause(standard_id=std.id, clause_number="13", title="Leakage Current",
                               content="Leakage current shall not exceed 0.5 mA for Class I appliances."),
                StandardClause(standard_id=std.id, clause_number="27", title="Earthing",
                               content="Class I appliances shall have effective earthing continuity."),
            ]
            for c in clauses:
                db.add(c)
            db.flush()
            req = Requirement(standard_id=std.id, clause_id=clauses[1].id,
                              requirement_number="13.1",
                              description="Leakage current not to exceed 0.5 mA.",
                              category="Safety")
            db.add(req)

        # Certification Schemes
        schemes = [
            CertificationScheme(
                scheme_name="BIS Product Certification (ISI Mark)",
                description="Mandatory or voluntary certification for products conforming to Indian Standards.",
                product_category="General",
                authority="Bureau of Indian Standards",
                process_description="Application → Testing at BIS-recognized lab → Factory inspection → License grant → Surveillance.",
            ),
            CertificationScheme(
                scheme_name="BIS Hallmarking",
                description="Mandatory hallmarking for gold jewellery sold in India.",
                product_category="Precious Metals",
                authority="Bureau of Indian Standards",
                process_description="Jeweller registration → Submission to Assaying & Hallmarking Centre → Testing → HUID assignment → Hallmark stamping.",
            ),
            CertificationScheme(
                scheme_name="BIS CRS (Compulsory Registration Scheme)",
                description="Registration scheme for electronics and IT products.",
                product_category="Electronics",
                authority="Bureau of Indian Standards",
                process_description="Application → Testing at BIS-recognized lab → Registration → R-number on product.",
            ),
        ]
        for s in schemes:
            db.add(s)

        db.commit()
        logger.info("Seeded clauses, requirements, and certification schemes.")
    except Exception:
        logger.exception("Failed to seed clauses/requirements")
        db.rollback()
    finally:
        db.close()


if __name__ == "__main__":
    seed_clauses_requirements()

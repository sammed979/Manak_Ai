"""
Seed laboratories and hallmarking centres.
Data is DEMO/UNVERIFIED — verify with NABL and BIS before use.
"""
from __future__ import annotations

import logging
import sys
from pathlib import Path

BACKEND_DIR = Path(__file__).resolve().parent
if str(BACKEND_DIR) not in sys.path:
    sys.path.insert(0, str(BACKEND_DIR))

from app.database.session import SessionLocal
from app.models.laboratory import Laboratory, LabType
from app.models.standard import AuthorityLevel
from app.models.hallmarking import HallmarkingCentre

logging.basicConfig(level=logging.INFO, format="[%(levelname)s] %(message)s")
logger = logging.getLogger("seed_labs")

DEMO_LABS = [
    {
        "name": "BIS Central Laboratory, New Delhi (DEMO)",
        "lab_type": LabType.BIS_RECOGNIZED,
        "city": "New Delhi",
        "state": "Delhi",
        "contact_email": "centrallab@bis.gov.in",
        "contact_phone": "+91-11-23237341",
        "website": "https://www.bis.gov.in",
        "scope_of_testing": "Electrical appliances, mechanical products, chemical analysis",
        "capabilities": '["Electrical Safety Testing", "EMI/EMC Testing", "Chemical Analysis", "Mechanical Testing"]',
        "verification_status": "DEMO",
        "authority_level": AuthorityLevel.UNVERIFIED,
    },
    {
        "name": "BIS Western Regional Laboratory, Mumbai (DEMO)",
        "lab_type": LabType.BIS_RECOGNIZED,
        "city": "Mumbai",
        "state": "Maharashtra",
        "contact_email": "wrl@bis.gov.in",
        "contact_phone": "+91-22-26543210",
        "website": "https://www.bis.gov.in",
        "scope_of_testing": "Chemical analysis, food testing, water quality, textiles",
        "capabilities": '["Chemical Analysis", "Food Testing", "Water Quality", "Textile Testing"]',
        "verification_status": "DEMO",
        "authority_level": AuthorityLevel.UNVERIFIED,
    },
    {
        "name": "BIS Southern Regional Laboratory, Chennai (DEMO)",
        "lab_type": LabType.BIS_RECOGNIZED,
        "city": "Chennai",
        "state": "Tamil Nadu",
        "contact_email": "srl@bis.gov.in",
        "contact_phone": "+91-44-23456789",
        "website": "https://www.bis.gov.in",
        "scope_of_testing": "Mechanical testing, metallurgy, construction materials",
        "capabilities": '["Mechanical Testing", "Metallurgy", "Non-Destructive Testing", "Construction Materials"]',
        "verification_status": "DEMO",
        "authority_level": AuthorityLevel.UNVERIFIED,
    },
    {
        "name": "BIS Eastern Regional Laboratory, Kolkata (DEMO)",
        "lab_type": LabType.BIS_RECOGNIZED,
        "city": "Kolkata",
        "state": "West Bengal",
        "contact_email": "erl@bis.gov.in",
        "contact_phone": "+91-33-23456789",
        "website": "https://www.bis.gov.in",
        "scope_of_testing": "Jute, textiles, food products, agricultural products",
        "capabilities": '["Jute Testing", "Textile Testing", "Food Testing", "Agricultural Products"]',
        "verification_status": "DEMO",
        "authority_level": AuthorityLevel.UNVERIFIED,
    },
]

DEMO_HALLMARKING_CENTRES = [
    {
        "centre_name": "BIS Hallmarking Centre, New Delhi (DEMO)",
        "city": "New Delhi",
        "state": "Delhi",
        "contact_phone": "+91-11-23237341",
        "verification_status": "DEMO",
    },
    {
        "centre_name": "BIS Hallmarking Centre, Mumbai (DEMO)",
        "city": "Mumbai",
        "state": "Maharashtra",
        "contact_phone": "+91-22-26543210",
        "verification_status": "DEMO",
    },
]


def seed_labs() -> None:
    db = SessionLocal()
    try:
        existing = db.query(Laboratory).count()
        if existing > 0:
            logger.info("Laboratories already seeded (%d records); skipping.", existing)
            return

        for lab_data in DEMO_LABS:
            lab = Laboratory(**lab_data)
            db.add(lab)

        db.commit()
        logger.info("Seeded %d demo laboratories.", len(DEMO_LABS))
        logger.info("NOTE: Lab data is DEMO — verify with NABL/BIS before use.")
    except Exception:
        logger.exception("Failed to seed labs")
        db.rollback()
    finally:
        db.close()


if __name__ == "__main__":
    seed_labs()

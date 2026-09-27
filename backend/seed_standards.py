"""
Seed standard metadata into the standards table.
Data is DEMO/UNVERIFIED — not official BIS information.
"""
from __future__ import annotations

import logging
import sys
from pathlib import Path

BACKEND_DIR = Path(__file__).resolve().parent
if str(BACKEND_DIR) not in sys.path:
    sys.path.insert(0, str(BACKEND_DIR))

from app.database.session import SessionLocal
from app.models.standard import Standard, StandardStatus, AuthorityLevel

logging.basicConfig(level=logging.INFO, format="[%(levelname)s] %(message)s")
logger = logging.getLogger("seed_standards")

STANDARDS = [
    # Food & Dairy
    dict(standard_number="IS 1166:1968", title="Specification for Curd (Dahi)",
         scope="Fermented dairy product — curd/dahi requirements",
         category="Food", subcategory="Dairy", status=StandardStatus.ACTIVE,
         authority_level=AuthorityLevel.UNVERIFIED, publication_date="1968-01-01"),
    dict(standard_number="IS 13334:1992", title="Specification for Dahi (Curd) — Skimmed and Partially Skimmed",
         scope="Skimmed and partially skimmed curd",
         category="Food", subcategory="Dairy", status=StandardStatus.ACTIVE,
         authority_level=AuthorityLevel.UNVERIFIED, publication_date="1992-01-01"),
    dict(standard_number="IS 1479:1961", title="Methods of Test for Dairy Industry",
         scope="Test methods for milk and milk products including curd",
         category="Food", subcategory="Dairy", status=StandardStatus.ACTIVE,
         authority_level=AuthorityLevel.UNVERIFIED, publication_date="1961-01-01"),
    dict(standard_number="IS 1224:1977", title="Specification for Pasteurised Milk",
         scope="Pasteurised cow and buffalo milk",
         category="Food", subcategory="Dairy", status=StandardStatus.ACTIVE,
         authority_level=AuthorityLevel.UNVERIFIED, publication_date="1977-01-01"),
    dict(standard_number="IS 14543:2016", title="Packaged Drinking Water — Specification",
         scope="Packaged drinking water in sealed containers",
         category="Food", subcategory="Beverages", status=StandardStatus.ACTIVE,
         authority_level=AuthorityLevel.UNVERIFIED, publication_date="2016-01-01"),
    # Household & Metals
    dict(standard_number="IS 17342:2020", title="Stainless Steel Water Bottles — Specification",
         scope="Domestic stainless steel water bottles 200-2000ml",
         category="Household", subcategory="Food Contact", status=StandardStatus.ACTIVE,
         authority_level=AuthorityLevel.UNVERIFIED, publication_date="2020-01-01"),
    dict(standard_number="IS 6911:2018", title="Stainless Steel Sheets, Plates and Strips for Pressure Purposes",
         scope="Stainless steel flat products for pressure vessels",
         category="Metals", subcategory="Steel", status=StandardStatus.ACTIVE,
         authority_level=AuthorityLevel.UNVERIFIED, publication_date="2018-01-01"),
    dict(standard_number="IS 1573:2019", title="Stainless Steel Utensils — Specification",
         scope="Stainless steel utensils for food contact",
         category="Household", subcategory="Utensils", status=StandardStatus.ACTIVE,
         authority_level=AuthorityLevel.UNVERIFIED, publication_date="2019-01-01"),
    # Electrical
    dict(standard_number="IS 302-1:2021", title="General Safety Requirements for Household Electrical Appliances",
         scope="Household electrical appliances up to 250V",
         category="Electrical", subcategory="Safety", status=StandardStatus.ACTIVE,
         authority_level=AuthorityLevel.UNVERIFIED, publication_date="2021-01-01"),
    dict(standard_number="IS 1293:2019", title="Plugs and Socket-Outlets for Domestic and Similar General Purposes",
         scope="Plugs and sockets rated up to 16A, 250V",
         category="Electrical", subcategory="Wiring Accessories", status=StandardStatus.ACTIVE,
         authority_level=AuthorityLevel.UNVERIFIED, publication_date="2019-01-01"),
    dict(standard_number="IS 16046:2018", title="LED Lamps for General Lighting Services",
         scope="LED lamps for general lighting up to 250V",
         category="Electrical", subcategory="Lighting", status=StandardStatus.ACTIVE,
         authority_level=AuthorityLevel.UNVERIFIED, publication_date="2018-01-01"),
    # Construction
    dict(standard_number="IS 269:2015", title="Ordinary Portland Cement — Specification",
         scope="OPC grades 33, 43, 53",
         category="Construction", subcategory="Cement", status=StandardStatus.ACTIVE,
         authority_level=AuthorityLevel.UNVERIFIED, publication_date="2015-01-01"),
    dict(standard_number="IS 1786:2008", title="High Strength Deformed Steel Bars for Concrete Reinforcement",
         scope="TMT bars and deformed steel bars for RCC",
         category="Construction", subcategory="Steel", status=StandardStatus.ACTIVE,
         authority_level=AuthorityLevel.UNVERIFIED, publication_date="2008-01-01"),
    # Safety
    dict(standard_number="IS 4151:2015", title="Protective Helmets for Scooter and Motorcycle Riders",
         scope="Protective helmets for two-wheeler riders",
         category="Safety", subcategory="Protective Equipment", status=StandardStatus.ACTIVE,
         authority_level=AuthorityLevel.UNVERIFIED, publication_date="2015-01-01"),
    # Precious Metals
    dict(standard_number="IS 1417:1999", title="Grades of Gold Alloys — Jewellery and Artefacts",
         scope="Gold alloy grades for jewellery",
         category="Precious Metals", subcategory="Gold", status=StandardStatus.ACTIVE,
         authority_level=AuthorityLevel.UNVERIFIED, publication_date="1999-01-01"),
    # Textiles
    dict(standard_number="IS 1954:1990", title="Specification for Woollen Blankets",
         scope="Woollen blankets for domestic use",
         category="Textiles", subcategory="Household Textiles", status=StandardStatus.ACTIVE,
         authority_level=AuthorityLevel.UNVERIFIED, publication_date="1990-01-01"),
]


def seed_standards() -> None:
    db = SessionLocal()
    try:
        existing = db.query(Standard).count()
        if existing > 0:
            logger.info("Standards already seeded (%d records); skipping.", existing)
            return

        for data in STANDARDS:
            std = Standard(**data)
            db.add(std)

        db.commit()
        logger.info("Seeded %d standards.", len(STANDARDS))
    except Exception:
        logger.exception("Failed to seed standards")
        db.rollback()
    finally:
        db.close()


if __name__ == "__main__":
    seed_standards()

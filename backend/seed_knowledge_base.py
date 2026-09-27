"""
Structured BIS knowledge seed.

Every knowledge record has rich metadata:
  standard_number, title, product_category, product_keywords, scope,
  clause_number, clause_title, content, document_type, standard_status,
  source_authority, last_verified.

Data is clearly labelled DEMO / UNVERIFIED where not from an official source.
"""
from __future__ import annotations

import asyncio
import logging
import sys
from pathlib import Path

BACKEND_DIR = Path(__file__).resolve().parent
if str(BACKEND_DIR) not in sys.path:
    sys.path.insert(0, str(BACKEND_DIR))

from app.database.session import SessionLocal
from app.models.knowledge import KnowledgeDocument, KnowledgeChunk, DocumentType
from app.models.standard import AuthorityLevel, Standard, StandardStatus
from app.knowledge.ingestion import DocumentIngestionService
from app.ai.embeddings import get_embedding_service

logging.basicConfig(level=logging.INFO, format="[%(levelname)s] %(message)s")
logger = logging.getLogger("seed_knowledge")

# ---------------------------------------------------------------------------
# Knowledge records
# Each record: (metadata_dict, content_text)
# metadata is stored per-chunk so retrieval can filter/boost on it.
# ---------------------------------------------------------------------------

KNOWLEDGE_RECORDS = [
    # -----------------------------------------------------------------------
    # FOOD & DAIRY
    # -----------------------------------------------------------------------
    (
        {
            "standard_number": "IS 1479:1961",
            "title": "Methods of Test for Dairy Industry - Rapid Examination of Milk",
            "product_category": "food",
            "product_keywords": "milk dairy curd dahi yogurt fermented",
            "document_type": "STANDARD",
            "standard_status": "ACTIVE",
            "source_authority": "UNVERIFIED_DEMO",
            "last_verified": "2024-01-01",
        },
        """IS 1479:1961 — Methods of Test for Dairy Industry: Rapid Examination of Milk.
Scope: This standard specifies rapid methods for examination of milk and milk products including curd (dahi), yogurt, and fermented dairy products.
Product Category: Food and Dairy.
Keywords: milk, curd, dahi, yogurt, dairy, fermented milk, pasteurised milk.
Clause 1 — Scope: Covers testing methods for raw milk, pasteurised milk, curd (dahi), and other dairy products.
Clause 3 — Acidity Test: The titratable acidity of curd shall be expressed as lactic acid percentage.
Clause 4 — Fat Content: Fat content of curd shall be determined by Gerber method.
Note: For food safety requirements, also refer to FSSAI regulations and IS 1166 for curd/dahi specifications.""",
    ),
    (
        {
            "standard_number": "IS 1166:1968",
            "title": "Specification for Curd (Dahi)",
            "product_category": "food",
            "product_keywords": "curd dahi yogurt dairy fermented milk food",
            "document_type": "STANDARD",
            "standard_status": "ACTIVE",
            "source_authority": "UNVERIFIED_DEMO",
            "last_verified": "2024-01-01",
        },
        """IS 1166:1968 — Specification for Curd (Dahi).
Scope: This Indian Standard specifies requirements for curd (dahi) — a fermented dairy product made from milk by lactic acid fermentation.
Product Category: Food, Dairy Products.
Keywords: curd, dahi, yogurt, fermented milk, dairy, lactic acid, milk product.
Clause 2 — Description: Curd (dahi) is the product obtained from pasteurised or boiled milk by souring, natural or otherwise, with or without the addition of any harmless lactic acid or other bacterial culture.
Clause 3 — Requirements:
  3.1 Milk Fat: Not less than 3.0 percent by mass for full-cream curd.
  3.2 Milk Solids-Not-Fat: Not less than 8.5 percent by mass.
  3.3 Acidity: Not less than 0.5 percent and not more than 1.5 percent (as lactic acid).
  3.4 The product shall be free from preservatives, colouring matter, and adulterants.
Clause 4 — Packing and Marking: Containers shall be clean, sound, and food-grade.
Certification: BIS certification for curd/dahi is not universally mandatory under a QCO as of the last verified date. Manufacturers may voluntarily obtain BIS certification. FSSAI licensing is mandatory for food businesses.
Related Standards: IS 1479 (test methods), FSSAI Food Safety and Standards Regulations.""",
    ),
    (
        {
            "standard_number": "IS 13334:1992",
            "title": "Specification for Dahi (Curd) — Skimmed and Partially Skimmed",
            "product_category": "food",
            "product_keywords": "curd dahi skimmed low fat dairy fermented",
            "document_type": "STANDARD",
            "standard_status": "ACTIVE",
            "source_authority": "UNVERIFIED_DEMO",
            "last_verified": "2024-01-01",
        },
        """IS 13334:1992 — Specification for Dahi (Curd) — Skimmed and Partially Skimmed.
Scope: Covers skimmed and partially skimmed curd (dahi) products.
Product Category: Food, Dairy.
Keywords: curd, dahi, skimmed curd, low fat curd, dairy, fermented milk.
Clause 3 — Requirements:
  3.1 Skimmed Dahi: Milk fat not more than 0.5 percent.
  3.2 Partially Skimmed Dahi: Milk fat between 0.5 and 3.0 percent.
  3.3 Acidity: 0.5 to 1.5 percent as lactic acid.
Related Standards: IS 1166 (full-cream curd), IS 1479 (test methods).""",
    ),
    (
        {
            "standard_number": "IS 1224:1977",
            "title": "Specification for Pasteurised Milk",
            "product_category": "food",
            "product_keywords": "milk pasteurised dairy food beverage",
            "document_type": "STANDARD",
            "standard_status": "ACTIVE",
            "source_authority": "UNVERIFIED_DEMO",
            "last_verified": "2024-01-01",
        },
        """IS 1224:1977 — Specification for Pasteurised Milk.
Scope: Specifies requirements for pasteurised cow milk, buffalo milk, and mixed milk.
Product Category: Food, Dairy.
Keywords: milk, pasteurised milk, dairy, cow milk, buffalo milk, food safety.
Clause 3 — Requirements: Fat content, SNF content, and microbiological standards.
Related Standards: IS 1166 (curd/dahi), IS 1479 (test methods for dairy).""",
    ),
    # -----------------------------------------------------------------------
    # STAINLESS STEEL & METALS
    # -----------------------------------------------------------------------
    (
        {
            "standard_number": "IS 17342:2020",
            "title": "Stainless Steel Water Bottles — Specification",
            "product_category": "household",
            "product_keywords": "stainless steel water bottle flask thermos household",
            "document_type": "STANDARD",
            "standard_status": "ACTIVE",
            "source_authority": "UNVERIFIED_DEMO",
            "last_verified": "2024-01-01",
        },
        """IS 17342:2020 — Stainless Steel Water Bottles — Specification.
Scope: This Indian Standard specifies requirements for stainless steel water bottles intended for domestic use, with capacity ranging from 200 ml to 2000 ml.
Product Category: Household, Food Contact Articles.
Keywords: stainless steel, water bottle, flask, thermos, household, food contact, drinking water.
Clause 4 — Materials: The bottle shall be made of food-grade stainless steel conforming to IS 6911 or equivalent grade (304 or 316 stainless steel).
Clause 5 — Design Requirements: The bottle shall have a leak-proof cap. Inner surface shall be smooth and free from crevices.
Clause 6 — Performance Requirements:
  6.1 Leak Test: No leakage when filled with water and inverted for 30 minutes.
  6.2 Thermal Insulation: Temperature retention as specified.
  6.3 Drop Test: No structural failure after drop from 1 metre.
Clause 7 — Marking: Manufacturer name, capacity, material grade, and country of origin.
Certification: BIS certification under IS 17342 may be voluntary unless covered by a specific QCO. Verify current QCO status with BIS.""",
    ),
    (
        {
            "standard_number": "IS 6911:2018",
            "title": "Stainless Steel Sheets, Plates and Strips for Pressure Purposes",
            "product_category": "metals",
            "product_keywords": "stainless steel sheet plate strip pressure vessel metal",
            "document_type": "STANDARD",
            "standard_status": "ACTIVE",
            "source_authority": "UNVERIFIED_DEMO",
            "last_verified": "2024-01-01",
        },
        """IS 6911:2018 — Stainless Steel Sheets, Plates and Strips for Pressure Purposes.
Scope: Covers stainless steel flat products for pressure vessel and general engineering applications.
Product Category: Metals, Steel.
Keywords: stainless steel, sheet, plate, strip, pressure vessel, engineering, metal.
Clause 4 — Grades: Austenitic grades 304, 304L, 316, 316L covered.
Clause 5 — Chemical Composition: Chromium 17-20%, Nickel 8-12% for grade 304.
Clause 6 — Mechanical Properties: Tensile strength, yield strength, elongation requirements.
Related Standards: IS 17342 (water bottles), IS 1573 (utensils).""",
    ),
    (
        {
            "standard_number": "IS 1573:2019",
            "title": "Stainless Steel Utensils — Specification",
            "product_category": "household",
            "product_keywords": "stainless steel utensil cookware vessel kitchen household food contact",
            "document_type": "STANDARD",
            "standard_status": "ACTIVE",
            "source_authority": "UNVERIFIED_DEMO",
            "last_verified": "2024-01-01",
        },
        """IS 1573:2019 — Stainless Steel Utensils — Specification.
Scope: Covers stainless steel utensils for food contact use including plates, bowls, cups, and cooking vessels.
Product Category: Household, Food Contact.
Keywords: stainless steel, utensil, cookware, vessel, kitchen, food contact, household.
Clause 3 — Material: Food-grade stainless steel (grade 304 minimum).
Clause 4 — Finish: Inner surface shall be smooth, free from pits and crevices.
Clause 5 — Migration Limits: Heavy metal migration shall not exceed prescribed limits.
Certification: BIS certification for stainless steel utensils may be mandatory under applicable QCO. Verify with BIS.""",
    ),
    # -----------------------------------------------------------------------
    # ELECTRICAL
    # -----------------------------------------------------------------------
    (
        {
            "standard_number": "IS 302-1:2021",
            "title": "General Safety Requirements for Household Electrical Appliances — Part 1",
            "product_category": "electrical",
            "product_keywords": "electrical appliance household safety voltage insulation",
            "document_type": "STANDARD",
            "standard_status": "ACTIVE",
            "source_authority": "UNVERIFIED_DEMO",
            "last_verified": "2024-01-01",
        },
        """IS 302-1:2021 — General Safety Requirements for Household Electrical Appliances — Part 1: General Requirements.
Scope: Applies to electrical appliances for household and similar use, rated voltage up to 250V AC single phase or 480V for other supplies.
Product Category: Electrical, Household Appliances.
Keywords: electrical appliance, household, safety, voltage, insulation, earthing, marking.
Clause 7 — Marking and Instructions: Each appliance shall be marked with rated voltage, rated power, manufacturer name, and model number.
Clause 13 — Leakage Current and Electric Strength: Leakage current shall not exceed 0.5 mA for Class I appliances.
Clause 16 — Resistance to Heat and Fire: Materials shall withstand specified temperature tests.
Clause 27 — Earthing: Class I appliances shall have effective earthing continuity.
Certification: BIS certification (ISI Mark) is MANDATORY for many household electrical appliances under the Electrical Appliances (Quality Control) Order. Verify the specific product category with BIS.""",
    ),
    (
        {
            "standard_number": "IS 1293:2019",
            "title": "Plugs and Socket-Outlets for Domestic and Similar General Purposes",
            "product_category": "electrical",
            "product_keywords": "plug socket outlet electrical domestic wiring",
            "document_type": "STANDARD",
            "standard_status": "ACTIVE",
            "source_authority": "UNVERIFIED_DEMO",
            "last_verified": "2024-01-01",
        },
        """IS 1293:2019 — Plugs and Socket-Outlets for Domestic and Similar General Purposes.
Scope: Covers plugs and socket-outlets rated up to 16A, 250V AC for domestic use.
Product Category: Electrical, Wiring Accessories.
Keywords: plug, socket, outlet, electrical, domestic, wiring, 5A, 15A, 16A.
Clause 4 — Ratings: 5A/250V and 15A/250V are standard Indian ratings.
Clause 8 — Dimensions: Pin dimensions and socket dimensions specified.
Clause 12 — Temperature Rise: Temperature rise shall not exceed 45K.
Certification: BIS certification is MANDATORY for plugs and socket-outlets under the Wiring Accessories (Quality Control) Order.""",
    ),
    (
        {
            "standard_number": "IS 16046:2018",
            "title": "LED Lamps for General Lighting Services — Performance Requirements",
            "product_category": "electrical",
            "product_keywords": "led lamp bulb lighting electrical energy efficiency",
            "document_type": "STANDARD",
            "standard_status": "ACTIVE",
            "source_authority": "UNVERIFIED_DEMO",
            "last_verified": "2024-01-01",
        },
        """IS 16046:2018 — LED Lamps for General Lighting Services — Performance Requirements.
Scope: Covers LED lamps intended for general lighting with supply voltage up to 250V.
Product Category: Electrical, Lighting.
Keywords: LED, lamp, bulb, lighting, energy efficiency, lumen, watt.
Clause 5 — Photometric Requirements: Luminous flux, luminous efficacy.
Clause 6 — Electrical Requirements: Power factor, total harmonic distortion.
Clause 7 — Lifetime: Rated lifetime and lumen maintenance.
Certification: BIS certification is MANDATORY for LED lamps under the LED Lights and Fixtures (Quality Control) Order.""",
    ),
    # -----------------------------------------------------------------------
    # CONSTRUCTION
    # -----------------------------------------------------------------------
    (
        {
            "standard_number": "IS 269:2015",
            "title": "Ordinary Portland Cement — Specification",
            "product_category": "construction",
            "product_keywords": "cement portland concrete construction building",
            "document_type": "STANDARD",
            "standard_status": "ACTIVE",
            "source_authority": "UNVERIFIED_DEMO",
            "last_verified": "2024-01-01",
        },
        """IS 269:2015 — Ordinary Portland Cement — Specification.
Scope: Specifies requirements for Ordinary Portland Cement (OPC) grades 33, 43, and 53.
Product Category: Construction Materials.
Keywords: cement, OPC, portland cement, concrete, construction, building material.
Clause 5 — Chemical Requirements: Lime saturation factor, silica ratio, alumina ratio.
Clause 6 — Physical Requirements: Fineness, soundness, setting time, compressive strength.
Certification: BIS certification (ISI Mark) is MANDATORY for cement under the Cement (Quality Control) Order.""",
    ),
    (
        {
            "standard_number": "IS 1786:2008",
            "title": "High Strength Deformed Steel Bars and Wires for Concrete Reinforcement",
            "product_category": "construction",
            "product_keywords": "steel rebar reinforcement concrete construction TMT bar",
            "document_type": "STANDARD",
            "standard_status": "ACTIVE",
            "source_authority": "UNVERIFIED_DEMO",
            "last_verified": "2024-01-01",
        },
        """IS 1786:2008 — High Strength Deformed Steel Bars and Wires for Concrete Reinforcement.
Scope: Covers TMT (Thermo-Mechanically Treated) bars and deformed steel bars for reinforced concrete.
Product Category: Construction, Steel.
Keywords: TMT bar, rebar, reinforcement, steel bar, concrete, construction, Fe415, Fe500.
Clause 5 — Grades: Fe415, Fe415D, Fe500, Fe500D, Fe550, Fe550D, Fe600.
Clause 6 — Chemical Composition: Carbon, sulphur, phosphorus limits.
Clause 7 — Mechanical Properties: Yield strength, tensile strength, elongation, bend test.
Certification: BIS certification is MANDATORY for TMT bars under the Steel and Steel Products (Quality Control) Order.""",
    ),
    # -----------------------------------------------------------------------
    # HELMETS & SAFETY
    # -----------------------------------------------------------------------
    (
        {
            "standard_number": "IS 4151:2015",
            "title": "Protective Helmets for Scooter and Motorcycle Riders",
            "product_category": "safety",
            "product_keywords": "helmet motorcycle scooter safety protective headgear",
            "document_type": "STANDARD",
            "standard_status": "ACTIVE",
            "source_authority": "UNVERIFIED_DEMO",
            "last_verified": "2024-01-01",
        },
        """IS 4151:2015 — Protective Helmets for Scooter and Motorcycle Riders.
Scope: Specifies requirements for protective helmets worn by riders of scooters and motorcycles.
Product Category: Safety Equipment, Automotive.
Keywords: helmet, motorcycle helmet, scooter helmet, safety, protective headgear, ISI helmet.
Clause 5 — Construction: Shell, retention system, visor requirements.
Clause 6 — Performance Tests: Impact absorption, penetration resistance, retention system strength.
Clause 7 — Marking: ISI Mark, manufacturer details, size, year of manufacture.
Certification: BIS certification (ISI Mark) is MANDATORY for motorcycle helmets under the Helmets (Quality Control) Order. Helmets without ISI Mark are illegal for sale in India.""",
    ),
    # -----------------------------------------------------------------------
    # HALLMARKING
    # -----------------------------------------------------------------------
    (
        {
            "standard_number": "IS 1417:1999",
            "title": "Grades of Gold Alloys — Jewellery and Artefacts",
            "product_category": "precious_metals",
            "product_keywords": "gold hallmark jewellery jewelry karat purity precious metal",
            "document_type": "STANDARD",
            "standard_status": "ACTIVE",
            "source_authority": "UNVERIFIED_DEMO",
            "last_verified": "2024-01-01",
        },
        """IS 1417:1999 — Grades of Gold Alloys — Jewellery and Artefacts.
Scope: Specifies grades of gold alloys used in jewellery and artefacts.
Product Category: Precious Metals, Jewellery.
Keywords: gold, hallmark, hallmarking, jewellery, jewelry, karat, carat, purity, HUID.
Clause 3 — Grades:
  14 Karat (585): 58.5% gold purity.
  18 Karat (750): 75.0% gold purity.
  22 Karat (916): 91.6% gold purity.
  24 Karat (999): 99.9% gold purity.
Hallmarking: BIS Hallmarking is MANDATORY for gold jewellery sold in India under the BIS (Hallmarking) Regulations. Every hallmarked article must carry: BIS Mark, Purity/Fineness, HUID (Hallmark Unique Identification).
HUID: A 6-character alphanumeric code assigned to each hallmarked jewellery piece for traceability.""",
    ),
    # -----------------------------------------------------------------------
    # CERTIFICATION & BIS GENERAL
    # -----------------------------------------------------------------------
    (
        {
            "document_type": "FAQ",
            "product_category": "general",
            "product_keywords": "bis certification isi mark mandatory voluntary",
            "source_authority": "UNVERIFIED_DEMO",
            "last_verified": "2024-01-01",
        },
        """FAQ: What is BIS Certification and the ISI Mark?

BIS (Bureau of Indian Standards) is India's national standards body established under the BIS Act, 2016.

ISI Mark: The Standard Mark granted by BIS to products that conform to the relevant Indian Standard. Products bearing the ISI Mark have been tested and certified by BIS.

Mandatory Certification: Certain products are required by law to carry the ISI Mark under Quality Control Orders (QCOs) issued by the Government of India. Examples include:
- Cement (IS 269, IS 8112, IS 455)
- TMT Steel Bars (IS 1786)
- Household Electrical Appliances (IS 302)
- Motorcycle Helmets (IS 4151)
- LED Lamps (IS 16046)
- Plugs and Sockets (IS 1293)

Voluntary Certification: For products not covered by a QCO, manufacturers may voluntarily obtain BIS certification to demonstrate quality.

How to apply: Submit application to BIS, get product tested at a BIS-recognized laboratory, undergo factory inspection. If compliant, BIS grants a license to use the Standard Mark.

Official BIS website: https://www.bis.gov.in""",
    ),
    (
        {
            "document_type": "FAQ",
            "product_category": "general",
            "product_keywords": "qco quality control order mandatory bis compulsory",
            "source_authority": "UNVERIFIED_DEMO",
            "last_verified": "2024-01-01",
        },
        """FAQ: What is a Quality Control Order (QCO)?

A Quality Control Order (QCO) is a government notification issued under the BIS Act or other legislation that makes BIS certification MANDATORY for specific products.

When a QCO is in force:
- The product cannot be manufactured, imported, or sold in India without a valid BIS license.
- The product must bear the ISI Mark.
- Violation is a criminal offence under the BIS Act, 2016.

QCOs are issued by the Ministry of Commerce and Industry or sector-specific ministries.

To check if a product is under a QCO: Visit https://www.bis.gov.in or the relevant ministry website.

Important: Not every Indian Standard has a corresponding QCO. The existence of an IS number does NOT automatically mean BIS certification is mandatory.""",
    ),
    (
        {
            "document_type": "FAQ",
            "product_category": "general",
            "product_keywords": "bis laboratory testing nabl accredited recognized",
            "source_authority": "UNVERIFIED_DEMO",
            "last_verified": "2024-01-01",
        },
        """FAQ: How to find a BIS-recognized or NABL-accredited laboratory?

For BIS certification testing, products must be tested at:
1. BIS own laboratories, OR
2. BIS-recognized laboratories (listed on BIS website), OR
3. NABL-accredited laboratories (for certain schemes).

NABL (National Accreditation Board for Testing and Calibration Laboratories) accredits laboratories under ISO/IEC 17025.

To find laboratories:
- BIS recognized labs: https://www.bis.gov.in (Laboratory Recognition section)
- NABL accredited labs: https://www.nabl-india.org

Important: Always verify current accreditation status directly with NABL or BIS before engaging a laboratory, as accreditation status can change.""",
    ),
    (
        {
            "document_type": "FAQ",
            "product_category": "general",
            "product_keywords": "bis hallmarking gold silver mandatory jewellery",
            "source_authority": "UNVERIFIED_DEMO",
            "last_verified": "2024-01-01",
        },
        """FAQ: Is BIS Hallmarking mandatory for gold jewellery in India?

Yes. BIS Hallmarking is MANDATORY for gold jewellery sold in India as per the BIS (Hallmarking) Regulations and subsequent government notifications.

Mandatory hallmarking applies to:
- Gold jewellery and artefacts of 14K, 18K, 20K, 22K, 23K, and 24K purity.
- Sold by jewellers registered with BIS.

HUID (Hallmark Unique Identification): Every hallmarked piece must carry a unique 6-character alphanumeric HUID for traceability.

Hallmark components on a piece:
1. BIS Mark (triangle logo)
2. Purity/Fineness (e.g., 916 for 22K)
3. HUID number

Silver hallmarking: Voluntary as of last verified date. Verify current status with BIS.

Official source: https://www.bis.gov.in (Hallmarking section)""",
    ),
    # -----------------------------------------------------------------------
    # PLASTICS & PACKAGING
    # -----------------------------------------------------------------------
    (
        {
            "standard_number": "IS 14543:2016",
            "title": "Packaged Drinking Water (Other than Mineral Water) — Specification",
            "product_category": "food",
            "product_keywords": "packaged drinking water bottled water food safety",
            "document_type": "STANDARD",
            "standard_status": "ACTIVE",
            "source_authority": "UNVERIFIED_DEMO",
            "last_verified": "2024-01-01",
        },
        """IS 14543:2016 — Packaged Drinking Water (Other than Mineral Water) — Specification.
Scope: Covers packaged drinking water sold in sealed containers.
Product Category: Food, Beverages, Packaged Water.
Keywords: packaged water, bottled water, drinking water, mineral water, food safety.
Clause 4 — Physical Requirements: Colour, odour, taste, turbidity.
Clause 5 — Chemical Requirements: pH, TDS, heavy metals, pesticide residues.
Clause 6 — Microbiological Requirements: Total coliform, E. coli, Salmonella.
Certification: BIS certification is MANDATORY for packaged drinking water under the Packaged Drinking Water (Quality Control) Order.""",
    ),
    # -----------------------------------------------------------------------
    # TEXTILES
    # -----------------------------------------------------------------------
    (
        {
            "standard_number": "IS 1954:1990",
            "title": "Specification for Woollen Blankets",
            "product_category": "textiles",
            "product_keywords": "blanket wool textile fabric clothing",
            "document_type": "STANDARD",
            "standard_status": "ACTIVE",
            "source_authority": "UNVERIFIED_DEMO",
            "last_verified": "2024-01-01",
        },
        """IS 1954:1990 — Specification for Woollen Blankets.
Scope: Covers woollen blankets for domestic use.
Product Category: Textiles, Household.
Keywords: blanket, wool, woollen, textile, fabric.
Clause 3 — Material: Wool content requirements.
Clause 4 — Dimensions: Standard sizes for single, double blankets.
Clause 5 — Physical Properties: Mass per unit area, tensile strength, colour fastness.""",
    ),
]


async def seed_knowledge_base() -> None:
    db = SessionLocal()
    try:
        embedding_service = get_embedding_service()
        ingestion_service = DocumentIngestionService(embedding_service, db)

        # Check if already seeded
        from app.models.knowledge import KnowledgeDocument
        existing = db.query(KnowledgeDocument).count()
        if existing > 0:
            logger.info("Knowledge base already has %d documents; skipping re-seed.", existing)
            return

        logger.info("Seeding %d knowledge records...", len(KNOWLEDGE_RECORDS))

        for i, (metadata, content) in enumerate(KNOWLEDGE_RECORDS):
            std_num = metadata.get("standard_number", "")
            title = metadata.get("title", f"Knowledge Record {i+1}")
            doc_type_str = metadata.get("document_type", "OTHER")

            try:
                doc_type = DocumentType[doc_type_str]
            except KeyError:
                doc_type = DocumentType.OTHER

            await ingestion_service.ingest_text(
                title=title,
                content=content,
                document_type=doc_type,
                source_name="BIS Demo Knowledge Base",
                authority_level=AuthorityLevel.UNVERIFIED,
                metadata=metadata,
            )
            logger.info("  [%d/%d] Ingested: %s", i + 1, len(KNOWLEDGE_RECORDS), title)

        logger.info("Knowledge base seeded successfully.")
        logger.info("NOTE: All data is DEMO/UNVERIFIED — not official BIS information.")
    except Exception:
        logger.exception("Failed to seed knowledge base")
        db.rollback()
    finally:
        db.close()


if __name__ == "__main__":
    asyncio.run(seed_knowledge_base())

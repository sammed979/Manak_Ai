"""
DEMO DATA SEED SCRIPT

This script creates demo/sample data for development purposes.
All data is clearly marked as DEMO DATA and NOT OFFICIAL BIS INFORMATION.
"""
import asyncio
from sqlalchemy.orm import Session
from app.database.session import SessionLocal, engine
from app.models.knowledge import KnowledgeDocument, DocumentType, AuthorityLevel
from app.models.standard import Standard, StandardStatus
from app.knowledge.ingestion import DocumentIngestionService
from app.ai.embeddings import MockEmbeddingService


async def seed_demo_data():
    db = SessionLocal()
    
    try:
        embedding_service = MockEmbeddingService()
        ingestion_service = DocumentIngestionService(embedding_service, db)
        
        print("Seeding demo data...")
        
        # Demo Standard 1 - Stainless Steel Water Bottles
        standard_content = """
        This Indian Standard specifies the requirements for stainless steel water bottles intended for domestic use.
        The standard covers materials, design, construction, performance requirements, and test methods.
        Scope: This standard applies to stainless steel water bottles with capacity ranging from 200 ml to 2000 ml.
        Materials: The bottle shall be made of food-grade stainless steel conforming to IS 6911 or equivalent.
        Design Requirements: The bottle shall have a leak-proof cap and allow easy cleaning.
        Performance Requirements: Leak test, thermal insulation, and drop test requirements apply.
        """
        
        await ingestion_service.ingest_standard(
            standard_number="IS 17342:2020",
            title="Stainless Steel Water Bottles - Specification",
            content=standard_content,
            scope="Domestic stainless steel water bottles 200-2000ml",
            authority_level=AuthorityLevel.UNVERIFIED
        )
        
        # Demo Standard 2 - Electrical Safety
        electrical_content = """
        This Indian Standard specifies safety requirements for electrical appliances.
        Scope: This standard applies to electrical appliances rated up to 250V AC for household use.
        Safety Requirements: Insulation resistance shall not be less than 2 MΩ. Earth continuity shall be maintained.
        Marking: Each appliance shall be marked with manufacturer name, rated voltage, and power consumption.
        """
        
        await ingestion_service.ingest_standard(
            standard_number="IS 302-1:2021",
            title="General Safety Requirements for Household Electrical Appliances",
            content=electrical_content,
            scope="Household electrical appliances up to 250V",
            authority_level=AuthorityLevel.UNVERIFIED
        )
        
        # Demo FAQ as documents
        await ingestion_service.ingest_text(
            title="FAQ: What is BIS certification?",
            content="Question: What is BIS certification?\nAnswer: BIS certification is a conformity assessment scheme that verifies that products meet Indian Standards. It involves testing, inspection, and quality system assessment. Products that meet the requirements are granted the BIS Standard Mark.",
            document_type=DocumentType.FAQ,
            authority_level=AuthorityLevel.VERIFIED_SECONDARY,
            metadata={"category": "Certification"}
        )
        
        await ingestion_service.ingest_text(
            title="FAQ: How do I get my product BIS certified?",
            content="Question: How do I get my product BIS certified?\nAnswer: To get BIS certification: 1) Identify applicable standards, 2) Submit application to BIS, 3) Get your product tested at BIS-recognized laboratory, 4) Undergo factory inspection, 5) If compliant, BIS grants license to use Standard Mark.",
            document_type=DocumentType.FAQ,
            authority_level=AuthorityLevel.VERIFIED_SECONDARY,
            metadata={"category": "Certification"}
        )
        
        await ingestion_service.ingest_text(
            title="FAQ: Mandatory vs Voluntary BIS Certification",
            content="Question: What is the difference between mandatory and voluntary BIS certification?\nAnswer: Mandatory certification is required by law for certain products (like electrical appliances, helmets, etc.) under BIS Act. Voluntary certification is optional and helps manufacturers demonstrate product quality and safety to consumers.",
            document_type=DocumentType.FAQ,
            authority_level=AuthorityLevel.VERIFIED_SECONDARY,
            metadata={"category": "Certification"}
        )
        
        # Demo General Information
        general_info = """
        BIS (Bureau of Indian Standards) is the national standards body of India.
        It formulates standards and promotes quality through certification schemes.
        Key BIS Services: Product Certification (ISI Mark), System Certification, Hallmarking for precious metals, Laboratory testing services.
        BIS operates under the Bureau of Indian Standards Act, 2016.
        """
        
        await ingestion_service.ingest_text(
            title="About BIS - Bureau of Indian Standards",
            content=general_info,
            document_type=DocumentType.GUIDELINE,
            authority_level=AuthorityLevel.VERIFIED_SECONDARY
        )
        
        db.commit()
        print("Demo data seeded successfully!")
        print("NOTE: This is DEMO DATA - NOT OFFICIAL BIS INFORMATION")
        
    except Exception as e:
        import traceback
        print(f"Error seeding demo data: {e}")
        traceback.print_exc()
        db.rollback()
    finally:
        db.close()


if __name__ == "__main__":
    asyncio.run(seed_demo_data())

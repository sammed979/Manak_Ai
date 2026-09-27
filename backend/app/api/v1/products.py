from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from uuid import UUID
from app.database.session import get_db
from app.schemas.product import (
    ProductCreate, ProductResponse, ProductStandardMatchResponse,
    ComplianceCheckCreate, ComplianceCheckResponse, ComplianceCheckItemUpdate
)
from app.models.product import Product, ProductStandardMatch
from app.models.standard import Standard
from app.models.user import User
from app.product.matching import ProductStandardMatcher
from app.product.compliance import ComplianceEngine
from app.ai.embeddings import MockEmbeddingService
from app.security.dependencies import get_current_user

router = APIRouter(prefix="/products", tags=["Products"])


@router.post("/", response_model=ProductResponse)
async def create_product(
    product_data: ProductCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Create a new product
    """
    try:
        product = Product(
            name=product_data.name,
            description=product_data.description,
            category=product_data.category,
            manufacturer_id=current_user.id,
            sku=product_data.sku,
            brand=product_data.brand,
            model=product_data.model,
            specifications=product_data.specifications,
            intended_use=product_data.intended_use,
            target_market=product_data.target_market
        )
        
        db.add(product)
        db.commit()
        db.refresh(product)
        
        return ProductResponse.model_validate(product)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to create product: {str(e)}"
        )


@router.get("/", response_model=list[ProductResponse])
async def list_products(
    skip: int = 0,
    limit: int = 100,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    List products (filter by manufacturer if not admin)
    """
    query = db.query(Product)
    
    if current_user.role.value != "ADMIN":
        query = query.filter(Product.manufacturer_id == current_user.id)
    
    products = query.offset(skip).limit(limit).all()
    return [ProductResponse.model_validate(p) for p in products]


@router.get("/{product_id}", response_model=ProductResponse)
async def get_product(
    product_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get a specific product
    """
    try:
        product_uuid = UUID(product_id)
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid product ID"
        )
    
    product = db.query(Product).filter(Product.id == product_uuid).first()
    
    if not product:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Product not found"
        )
    
    # Check access
    if current_user.role.value != "ADMIN" and product.manufacturer_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied"
        )
    
    return ProductResponse.model_validate(product)


@router.post("/{product_id}/match-standards", response_model=list[ProductStandardMatchResponse])
async def match_product_standards(
    product_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Match a product to applicable standards
    """
    try:
        product_uuid = UUID(product_id)
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid product ID"
        )
    
    product = db.query(Product).filter(Product.id == product_uuid).first()
    
    if not product:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Product not found"
        )
    
    # Check access
    if current_user.role.value != "ADMIN" and product.manufacturer_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied"
        )
    
    try:
        embedding_service = MockEmbeddingService()
        matcher = ProductStandardMatcher(embedding_service, db)
        
        matches = await matcher.match_product_to_standards(product)
        
        # Save matches
        matcher.save_matches(matches)
        
        return [ProductStandardMatchResponse.model_validate(m) for m in matches]
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Matching failed: {str(e)}"
        )


@router.get("/{product_id}/matches", response_model=list[ProductStandardMatchResponse])
async def get_product_matches(
    product_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get existing standard matches for a product
    """
    try:
        product_uuid = UUID(product_id)
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid product ID"
        )
    
    product = db.query(Product).filter(Product.id == product_uuid).first()
    
    if not product:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Product not found"
        )
    
    # Check access
    if current_user.role.value != "ADMIN" and product.manufacturer_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied"
        )
    
    matches = db.query(ProductStandardMatch).filter(
        ProductStandardMatch.product_id == product_uuid
    ).all()
    
    return [ProductStandardMatchResponse.model_validate(m) for m in matches]


@router.post("/{product_id}/compliance-checks", response_model=ComplianceCheckResponse)
async def create_compliance_check(
    product_id: str,
    check_data: ComplianceCheckCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Create a compliance check for a product
    """
    try:
        product_uuid = UUID(product_id)
        standard_uuid = UUID(str(check_data.standard_id))
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid ID format"
        )
    
    product = db.query(Product).filter(Product.id == product_uuid).first()
    
    if not product:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Product not found"
        )
    
    standard = db.query(Standard).filter(Standard.id == standard_uuid).first()
    
    if not standard:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Standard not found"
        )
    
    # Check access
    if current_user.role.value != "ADMIN" and product.manufacturer_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied"
        )
    
    try:
        compliance_engine = ComplianceEngine(db)
        compliance_check = compliance_engine.create_compliance_check(
            product=product,
            standard=standard,
            check_type=check_data.check_type,
            checked_by=current_user
        )
        
        return ComplianceCheckResponse.model_validate(compliance_check)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to create compliance check: {str(e)}"
        )


@router.get("/{product_id}/compliance-checks")
async def get_compliance_summary(
    product_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get compliance summary for a product
    """
    try:
        product_uuid = UUID(product_id)
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid product ID"
        )
    
    product = db.query(Product).filter(Product.id == product_uuid).first()
    
    if not product:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Product not found"
        )
    
    # Check access
    if current_user.role.value != "ADMIN" and product.manufacturer_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied"
        )
    
    compliance_engine = ComplianceEngine(db)
    summary = compliance_engine.get_compliance_summary(product_uuid)
    
    return summary

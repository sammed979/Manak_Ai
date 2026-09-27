from typing import List, Dict, Any, Optional
from sqlalchemy.orm import Session
from app.models.product import Product, ComplianceCheck, ComplianceCheckItem
from app.models.standard import Standard, Requirement
from app.models.user import User
from datetime import datetime


class ComplianceEngine:
    def __init__(self, db: Session):
        self.db = db
    
    def create_compliance_check(
        self,
        product: Product,
        standard: Standard,
        check_type: str = "INITIAL",
        checked_by: Optional[User] = None
    ) -> ComplianceCheck:
        """
        Create a new compliance check for a product against a standard
        """
        from app.models.product import ComplianceCheck
        
        compliance_check = ComplianceCheck(
            product_id=product.id,
            standard_id=standard.id,
            check_type=check_type,
            status="PENDING",
            checked_at=datetime.now().isoformat(),
            checked_by=checked_by.id if checked_by else None
        )
        
        self.db.add(compliance_check)
        self.db.flush()
        
        # Create check items for each requirement
        requirements = self.db.query(Requirement).filter(
            Requirement.standard_id == standard.id
        ).all()
        
        for requirement in requirements:
            check_item = ComplianceCheckItem(
                compliance_check_id=compliance_check.id,
                requirement_id=requirement.id,
                clause_reference=requirement.requirement_number,
                description=requirement.description,
                status="PENDING"
            )
            self.db.add(check_item)
        
        self.db.commit()
        self.db.refresh(compliance_check)
        
        return compliance_check
    
    def update_check_item(
        self,
        check_item_id: str,
        status: str,
        evidence: Optional[str] = None,
        notes: Optional[str] = None
    ) -> ComplianceCheckItem:
        """
        Update a compliance check item
        """
        check_item = self.db.query(ComplianceCheckItem).filter(
            ComplianceCheckItem.id == check_item_id
        ).first()
        
        if not check_item:
            raise ValueError("Check item not found")
        
        check_item.status = status
        if evidence:
            check_item.evidence = evidence
        if notes:
            check_item.notes = notes
        
        self.db.commit()
        self.db.refresh(check_item)
        
        # Update overall compliance check status
        self._update_compliance_check_status(check_item.compliance_check_id)
        
        return check_item
    
    def _update_compliance_check_status(self, compliance_check_id: str):
        """
        Update the overall compliance check status based on check items
        """
        compliance_check = self.db.query(ComplianceCheck).filter(
            ComplianceCheck.id == compliance_check_id
        ).first()
        
        if not compliance_check:
            return
        
        check_items = self.db.query(ComplianceCheckItem).filter(
            ComplianceCheckItem.compliance_check_id == compliance_check_id
        ).all()
        
        if not check_items:
            return
        
        # Calculate status
        statuses = [item.status for item in check_items]
        
        if all(s == "PASSED" for s in statuses):
            compliance_check.status = "PASSED"
            compliance_check.overall_score = 1.0
        elif any(s == "FAILED" for s in statuses):
            compliance_check.status = "FAILED"
            passed_count = sum(1 for s in statuses if s == "PASSED")
            total_count = len(statuses)
            compliance_check.overall_score = passed_count / total_count if total_count > 0 else 0
        elif all(s == "NOT_APPLICABLE" for s in statuses):
            compliance_check.status = "INCOMPLETE"
            compliance_check.overall_score = None
        else:
            compliance_check.status = "INCOMPLETE"
            passed_count = sum(1 for s in statuses if s == "PASSED")
            total_count = len(statuses)
            compliance_check.overall_score = passed_count / total_count if total_count > 0 else 0
        
        self.db.commit()
    
    def get_compliance_summary(
        self,
        product_id: str
    ) -> Dict[str, Any]:
        """
        Get a summary of compliance checks for a product
        """
        from uuid import UUID
        
        try:
            product_uuid = UUID(product_id)
        except ValueError:
            raise ValueError("Invalid product ID")
        
        compliance_checks = self.db.query(ComplianceCheck).filter(
            ComplianceCheck.product_id == product_uuid
        ).all()
        
        summary = {
            "total_checks": len(compliance_checks),
            "passed": 0,
            "failed": 0,
            "pending": 0,
            "incomplete": 0,
            "checks": []
        }
        
        for check in compliance_checks:
            summary["checks"].append({
                "id": str(check.id),
                "standard_id": str(check.standard_id),
                "status": check.status,
                "overall_score": check.overall_score,
                "checked_at": check.checked_at
            })
            
            if check.status == "PASSED":
                summary["passed"] += 1
            elif check.status == "FAILED":
                summary["failed"] += 1
            elif check.status == "PENDING":
                summary["pending"] += 1
            elif check.status == "INCOMPLETE":
                summary["incomplete"] += 1
        
        return summary
    
    def get_check_details(
        self,
        compliance_check_id: str
    ) -> Dict[str, Any]:
        """
        Get detailed information about a compliance check
        """
        compliance_check = self.db.query(ComplianceCheck).filter(
            ComplianceCheck.id == compliance_check_id
        ).first()
        
        if not compliance_check:
            raise ValueError("Compliance check not found")
        
        check_items = self.db.query(ComplianceCheckItem).filter(
            ComplianceCheckItem.compliance_check_id == compliance_check_id
        ).all()
        
        return {
            "id": str(compliance_check.id),
            "product_id": str(compliance_check.product_id),
            "standard_id": str(compliance_check.standard_id),
            "status": compliance_check.status,
            "overall_score": compliance_check.overall_score,
            "check_type": compliance_check.check_type,
            "checked_at": compliance_check.checked_at,
            "notes": compliance_check.notes,
            "items": [
                {
                    "id": str(item.id),
                    "requirement_id": str(item.requirement_id),
                    "clause_reference": item.clause_reference,
                    "description": item.description,
                    "status": item.status,
                    "evidence": item.evidence,
                    "notes": item.notes
                }
                for item in check_items
            ]
        }

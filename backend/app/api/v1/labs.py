"""
Laboratory search API — queries the actual database.
"""
from __future__ import annotations

from typing import Any, Dict, List, Optional

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.database.session import get_db
from app.models.laboratory import Laboratory

router = APIRouter(prefix="/labs", tags=["Laboratories"])


@router.get("/")
async def search_labs(
    q: Optional[str] = Query(None, description="Search by name or specialty"),
    city: Optional[str] = Query(None),
    lab_type: Optional[str] = Query(None),
    skip: int = 0,
    limit: int = 50,
    db: Session = Depends(get_db),
) -> Dict[str, Any]:
    """Search laboratories from the database."""
    query = db.query(Laboratory)

    if q:
        q_lower = f"%{q.lower()}%"
        query = query.filter(
            Laboratory.name.ilike(q_lower)
            | Laboratory.scope_of_testing.ilike(q_lower)
            | Laboratory.capabilities.ilike(q_lower)
        )

    if city:
        query = query.filter(Laboratory.city.ilike(f"%{city}%"))

    if lab_type:
        query = query.filter(Laboratory.lab_type == lab_type)

    total = query.count()
    labs = query.offset(skip).limit(limit).all()

    return {
        "total": total,
        "labs": [_lab_to_dict(lab) for lab in labs],
        "note": (
            "Laboratory data is from the indexed knowledge base. "
            "Verify accreditation status directly with NABL (https://www.nabl-india.org) "
            "or BIS (https://www.bis.gov.in) before engaging any laboratory."
        ),
    }


def _lab_to_dict(lab: Laboratory) -> Dict[str, Any]:
    import json
    capabilities = []
    if lab.capabilities:
        try:
            capabilities = json.loads(lab.capabilities)
        except Exception:
            capabilities = [lab.capabilities]

    return {
        "id": str(lab.id),
        "name": lab.name,
        "lab_type": lab.lab_type.value if lab.lab_type else None,
        "city": lab.city,
        "state": lab.state,
        "country": lab.country,
        "contact_email": lab.contact_email,
        "contact_phone": lab.contact_phone,
        "website": lab.website,
        "nabl_accreditation_number": lab.nabl_accreditation_number,
        "bis_recognition_number": lab.bis_recognition_number,
        "scope_of_testing": lab.scope_of_testing,
        "capabilities": capabilities,
        "verification_status": lab.verification_status,
        "authority_level": lab.authority_level.value if lab.authority_level else None,
    }

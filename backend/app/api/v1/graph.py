"""
Knowledge graph API — returns real database relationships.
"""
from __future__ import annotations

from typing import Any, Dict, List

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.database.session import get_db
from app.models.standard import Standard, StandardClause, Requirement, CertificationScheme

router = APIRouter(prefix="/graph", tags=["Knowledge Graph"])


@router.get("/")
async def get_knowledge_graph(db: Session = Depends(get_db)) -> Dict[str, Any]:
    """
    Return graph nodes and edges from actual database relationships.
    """
    nodes: List[Dict[str, Any]] = []
    edges: List[Dict[str, Any]] = []
    node_ids: set = set()

    def add_node(node_id: str, label: str, node_type: str, category: str = ""):
        if node_id not in node_ids:
            nodes.append({"id": node_id, "label": label, "type": node_type, "category": category})
            node_ids.add(node_id)

    standards = db.query(Standard).limit(20).all()
    for std in standards:
        sid = f"std_{std.id}"
        add_node(sid, std.standard_number, "standard", std.category or "")

        clauses = db.query(StandardClause).filter(StandardClause.standard_id == std.id).limit(5).all()
        for clause in clauses:
            cid = f"clause_{clause.id}"
            add_node(cid, f"Clause {clause.clause_number}", "clause", clause.title or "")
            edges.append({"from": sid, "to": cid, "label": "has_clause"})

            reqs = db.query(Requirement).filter(Requirement.clause_id == clause.id).limit(3).all()
            for req in reqs:
                rid = f"req_{req.id}"
                add_node(rid, f"Req {req.requirement_number or req.id}", "requirement", req.category or "")
                edges.append({"from": cid, "to": rid, "label": "has_requirement"})

    schemes = db.query(CertificationScheme).limit(5).all()
    for scheme in schemes:
        scid = f"scheme_{scheme.id}"
        add_node(scid, scheme.scheme_name[:30], "scheme", scheme.product_category or "")

    return {
        "nodes": nodes,
        "edges": edges,
        "stats": {
            "total_nodes": len(nodes),
            "total_edges": len(edges),
            "standards": sum(1 for n in nodes if n["type"] == "standard"),
            "clauses": sum(1 for n in nodes if n["type"] == "clause"),
            "requirements": sum(1 for n in nodes if n["type"] == "requirement"),
            "schemes": sum(1 for n in nodes if n["type"] == "scheme"),
        },
    }

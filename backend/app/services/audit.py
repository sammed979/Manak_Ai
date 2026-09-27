from __future__ import annotations

from typing import Any, Dict, Optional
from uuid import UUID
from app.models.audit import AdminAuditLog
from sqlalchemy.orm import Session
import logging

logger = logging.getLogger(__name__)


def log_action(
    db: Session,
    action: str,
    actor_id: Optional[UUID] = None,
    target_type: Optional[str] = None,
    target_id: Optional[str] = None,
    detail: Optional[str] = None,
    meta: Optional[Dict[str, Any]] = None,
    ip_address: Optional[str] = None,
) -> None:
    try:
        entry = AdminAuditLog(
            actor_id=actor_id,
            action=action,
            target_type=target_type,
            target_id=str(target_id) if target_id is not None else None,
            detail=detail,
            meta=meta,
            ip_address=ip_address,
        )
        db.add(entry)
        db.commit()
    except Exception:  # noqa: BLE001
        # Never let audit-log failures break the request.
        logger.exception("Failed to write audit log for action=%s", action)
        try:
            db.rollback()
        except Exception:
            pass

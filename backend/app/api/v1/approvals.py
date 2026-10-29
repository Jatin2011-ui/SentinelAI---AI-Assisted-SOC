
"""Approval workflow API (RBAC-protected)."""
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy.orm import Session

from app.api.deps import require_analyst
from app.db.session import get_db
from app.models.agent import Approval, ResponseAction
from app.services.response.actions import create_response_action

router = APIRouter()


class ResponseActionCreate(BaseModel):
    incident_id: str
    action_type: str
    params: dict = {}
    risk_class: str = "LOW"
    simulation: bool | None = None


@router.post("/responses")
def propose_action(
    payload: ResponseActionCreate,
    db: Session = Depends(get_db),
    user=Depends(require_analyst),
):
    action = create_response_action(
        db,
        incident_id=payload.incident_id,
        action_type=payload.action_type,
        params=payload.params,
        risk_class=payload.risk_class,
        simulation=payload.simulation,
    )
    return {"action_id": action.id, "status": action.status, "simulation": action.simulation}


class ApprovalDecision(BaseModel):
    decision: str  # APPROVED / REJECTED
    reason: str = ""


@router.post("/responses/{action_id}/approve")
def approve_action(
    action_id: str,
    decision: ApprovalDecision,
    db: Session = Depends(get_db),
    user=Depends(require_analyst),
):
    action = db.get(ResponseAction, action_id)
    if not action:
        raise HTTPException(status_code=404, detail="Action not found")
    approval = Approval(
        response_action_id=action_id,
        approver_id=user.id,
        decision=decision.decision.upper(),
        reason=decision.reason,
    )
    db.add(approval)
    if decision.decision.upper() == "APPROVED":
        action.status = "EXECUTED"
        action.result = {"executed": True, "simulated": action.simulation}
    else:
        action.status = "REJECTED"
    db.commit()
    return {"action_id": action_id, "status": action.status}

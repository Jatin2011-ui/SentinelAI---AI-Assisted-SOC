
"""Response action creation with approval gate and simulation."""
from app.core.config import get_settings
from app.models.agent import ResponseAction, Approval
from app.models.audit import AuditLog


def requires_approval(risk_class: str) -> bool:
    return risk_class in ("HIGH", "CRITICAL")


def create_response_action(db, incident_id: str, action_type: str, params: dict, risk_class: str, simulation: bool = None):
    settings = get_settings()
    simulation = simulation if simulation is not None else settings.simulation_mode
    action = ResponseAction(
        incident_id=incident_id,
        action_type=action_type,
        params=params,
        risk_class=risk_class,
        simulation=simulation,
        status="PENDING_APPROVAL" if requires_approval(risk_class) else "EXECUTED",
        result={"simulated": simulation},
    )
    db.add(action)
    db.commit()
    db.refresh(action)
    # audit log
    log = AuditLog(
        user_id=None,
        agent="ResponseAgent",
        action=action_type,
        tool="response_action",
        input_hash="",
        result="created",
        approval="PENDING" if requires_approval(risk_class) else "AUTO",
        status=action.status,
    )
    db.add(log)
    db.commit()
    return action


"""Agent orchestration API."""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.models.incident import Incident
from app.agents.state import SOCState
from app.agents.supervisor import SupervisorAgent

router = APIRouter()


@router.post("/incidents/{incident_id}/investigate")
def investigate_incident(incident_id: str, db: Session = Depends(get_db)):
    inc = db.get(Incident, incident_id)
    if not inc:
        raise HTTPException(status_code=404, detail="Incident not found")
    state = SOCState(
        incident_id=incident_id,
        incident={"id": inc.id, "title": inc.title, "severity": inc.severity},
        events=[],
    )
    supervisor = SupervisorAgent()
    state = supervisor.plan_investigation(state)
    state = supervisor.coordinate(state)
    return {"incident_id": incident_id, "state": state.model_dump()}

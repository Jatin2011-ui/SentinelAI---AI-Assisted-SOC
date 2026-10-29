
"""Incident correlation API."""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.models.incident import Incident
from app.services.incidents.correlator import correlate_events

router = APIRouter()


@router.post("/incidents/correlate")
def run_correlation(window_minutes: int = 30, min_events: int = 3, db: Session = Depends(get_db)):
    incidents = correlate_events(db, window_minutes=window_minutes, min_events=min_events)
    return {"created": len(incidents), "incidents": [i.id for i in incidents]}


@router.get("/incidents")
def list_incidents(db: Session = Depends(get_db)):
    incidents = db.query(Incident).order_by(Incident.created_at.desc()).all()
    return incidents


@router.get("/incidents/{incident_id}")
def get_incident(incident_id: str, db: Session = Depends(get_db)):
    inc = db.get(Incident, incident_id)
    if not inc:
        raise HTTPException(status_code=404, detail="Incident not found")
    return inc

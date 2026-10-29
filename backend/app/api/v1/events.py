
"""Event ingestion API."""
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.models.event import SecurityEvent
from app.schemas.events import EventIngest, EventResponse
from app.services.events.normalizer import normalize_event
from app.services.ml.features import build_feature_vector, store_features

router = APIRouter()


@router.post("/events", response_model=EventResponse, status_code=201)
def ingest_event(payload: EventIngest, db: Session = Depends(get_db)):
    event = normalize_event(payload, raw_payload=payload.model_dump(mode="json"))
    db.add(event)
    db.commit()
    db.refresh(event)
    return event


@router.get("/events", response_model=list[EventResponse])
def list_events(
    limit: int = Query(100, ge=1, le=1000),
    offset: int = Query(0, ge=0),
    event_type: str | None = Query(None),
    source_ip: str | None = Query(None),
    username: str | None = Query(None),
    db: Session = Depends(get_db),
):
    query = db.query(SecurityEvent)
    if event_type:
        query = query.filter(SecurityEvent.event_type == event_type)
    if source_ip:
        query = query.filter(SecurityEvent.source_ip == source_ip)
    if username:
        query = query.filter(SecurityEvent.username == username)
    events = query.order_by(SecurityEvent.timestamp.desc()).offset(offset).limit(limit).all()
    return events


@router.get("/events/{event_id}", response_model=EventResponse)
def get_event(event_id: str, db: Session = Depends(get_db)):
    event = db.get(SecurityEvent, event_id)
    if not event:
        raise HTTPException(status_code=404, detail="Event not found")
    return event


@router.post("/events/{event_id}/features")
def extract_features(event_id: str, window_hours: int = 1, db: Session = Depends(get_db)):
    event = db.get(SecurityEvent, event_id)
    if not event:
        raise HTTPException(status_code=404, detail="Event not found")
    vector = build_feature_vector(db, event, window_hours=window_hours)
    rec = store_features(db, event, vector, feature_version=vector.get("feature_version", "v1"))
    return {"event_id": event_id, "feature_id": rec.id, "vector": vector}


"""Rule-based event correlation engine.

Groups unlinked security events by entity (user / source IP / host) and
clusters them by time proximity on the event *timestamp* (not row creation
time, so historical event feeds correlate correctly). A cluster becomes an
incident when it reaches `min_events` or matches the brute-force pattern
(>= 5 auth failures followed by >= 1 success for the same entity).
"""
from collections import defaultdict
from datetime import timedelta

from sqlalchemy.orm import Session

from app.models.common import IncidentStatus, Severity
from app.models.event import SecurityEvent
from app.models.incident import Incident, IncidentEvent

# Do not attempt to correlate the entire table; cap the working set.
MAX_EVENTS_PER_RUN = 5000


def _group_events(events: list[SecurityEvent]) -> dict[tuple, list[SecurityEvent]]:
    """Group events by (username, source_ip, hostname)."""
    groups: dict[tuple, list[SecurityEvent]] = defaultdict(list)
    for e in events:
        key = (e.username or "unknown", e.source_ip or "unknown", e.hostname or "unknown")
        groups[key].append(e)
    return groups


def _cluster_by_time(events: list[SecurityEvent], window_minutes: int) -> list[list[SecurityEvent]]:
    """Split a group into clusters where each event is within window_minutes
    of the first event of its cluster (gap-based clustering on timestamp)."""
    ordered = sorted(events, key=lambda e: e.timestamp)
    clusters: list[list[SecurityEvent]] = []
    current: list[SecurityEvent] = []
    for e in ordered:
        if current and (e.timestamp - current[0].timestamp) > timedelta(minutes=window_minutes):
            clusters.append(current)
            current = []
        current.append(e)
    if current:
        clusters.append(current)
    return clusters


def _is_brute_force(evs: list[SecurityEvent]) -> bool:
    fails = sum(1 for e in evs if e.event_type == "authentication_failure")
    successes = sum(1 for e in evs if e.event_type == "authentication_success")
    return fails >= 5 and successes >= 1


def correlate_events(db: Session, window_minutes: int = 30, min_events: int = 3) -> list[Incident]:
    linked_event_ids = {ie.event_id for ie in db.query(IncidentEvent).all()}
    events = (
        db.query(SecurityEvent)
        .order_by(SecurityEvent.timestamp.desc())
        .limit(MAX_EVENTS_PER_RUN)
        .all()
    )
    events = [e for e in events if e.event_id not in linked_event_ids]
    if not events:
        return []

    groups = _group_events(events)
    created: list[Incident] = []
    for (user, ip, host), evs in groups.items():
        for cluster in _cluster_by_time(evs, window_minutes):
            if len(cluster) < min_events and not _is_brute_force(cluster):
                continue
            # "unknown" placeholder must not leak into the title.
            subject = next((v for v in (user, host, ip) if v != "unknown"), "unknown entity")
            severity = Severity.HIGH.value if _is_brute_force(cluster) else Severity.MEDIUM.value
            incident = Incident(
                title=f"Correlated events for {subject}",
                description=f"{len(cluster)} events correlated within {window_minutes} minutes",
                severity=severity,
                risk_score=min(100.0, len(cluster) * 10.0),
                confidence=0.7,
                status=IncidentStatus.NEW.value,
                affected_assets=[{"user": user, "ip": ip, "host": host}],
            )
            db.add(incident)
            db.flush()
            for e in cluster:
                db.add(IncidentEvent(incident_id=incident.id, event_id=e.event_id, weight=1.0))
            created.append(incident)
    db.commit()
    return created

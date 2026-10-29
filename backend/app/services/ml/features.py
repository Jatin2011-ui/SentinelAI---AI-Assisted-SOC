
"""Feature engineering for security events."""
from collections import defaultdict
from datetime import datetime, timedelta, timezone
from typing import List

from sqlalchemy.orm import Session

from app.models.event import SecurityEvent, FeatureRecord


def _window_events(db: Session, subject_key: str, subject_type: str, hours: int = 1):
    cutoff = datetime.now(timezone.utc) - timedelta(hours=hours)
    query = db.query(SecurityEvent).filter(SecurityEvent.created_at >= cutoff)
    if subject_type == "user":
        query = query.filter(SecurityEvent.username == subject_key)
    elif subject_type == "host":
        query = query.filter(SecurityEvent.hostname == subject_key)
    elif subject_type == "ip":
        query = query.filter(SecurityEvent.source_ip == subject_key)
    return query.all()


def extract_auth_features(events: List[SecurityEvent]) -> dict:
    failed = sum(1 for e in events if e.event_type == "authentication_failure")
    success = sum(1 for e in events if e.event_type == "authentication_success")
    ratio = failed / success if success else float(failed)
    uniq_ips = len({e.source_ip for e in events if e.source_ip})
    return {
        "auth_failed_count": failed,
        "auth_success_count": success,
        "auth_failure_success_ratio": ratio,
        "auth_unique_source_ip_count": uniq_ips,
    }


def extract_network_features(events: List[SecurityEvent]) -> dict:
    dest_diversity = len({e.destination_ip for e in events if e.destination_ip})
    port_diversity = len({e.destination_port for e in events if e.destination_port})
    protocol_counts = defaultdict(int)
    for e in events:
        if e.protocol:
            protocol_counts[e.protocol] += 1
    return {
        "network_dest_ip_diversity": dest_diversity,
        "network_port_diversity": port_diversity,
        "network_protocol_counts": dict(protocol_counts),
    }


def extract_process_features(events: List[SecurityEvent]) -> dict:
    proc_counts = defaultdict(int)
    for e in events:
        if e.process_name:
            proc_counts[e.process_name] += 1
    return {
        "process_frequency": dict(proc_counts),
    }


def build_feature_vector(db: Session, event: SecurityEvent, window_hours: int = 1) -> dict:
    # Determine subject
    subject_type = "user"
    subject_key = event.username or event.hostname or event.source_ip or "unknown"
    if not event.username:
        subject_type = "host"
        subject_key = event.hostname or event.source_ip or "unknown"
    if not subject_key or subject_key == "unknown":
        subject_type = "event"
        subject_key = event.event_id

    window = _window_events(db, subject_key, subject_type, hours=window_hours)
    features = {}
    features.update(extract_auth_features(window))
    features.update(extract_network_features(window))
    features.update(extract_process_features(window))
    features["event_type"] = event.event_type
    features["severity"] = event.severity
    features["hour_of_day"] = event.timestamp.hour
    features["feature_version"] = "v1"
    return features


def resolve_subject(event: SecurityEvent) -> tuple[str, str]:
    """Resolve the feature subject (user preferred, then host, then ip, then event)."""
    if event.username:
        return "user", event.username
    if event.hostname:
        return "host", event.hostname
    if event.source_ip:
        return "ip", event.source_ip
    return "event", event.event_id


def store_features(db: Session, event: SecurityEvent, vector: dict, feature_version: str = "v1"):
    subject_type, subject_key = resolve_subject(event)
    rec = FeatureRecord(
        event_id=event.event_id,
        subject_type=subject_type,
        subject_key=subject_key,
        feature_version=feature_version,
        vector=vector,
    )
    db.add(rec)
    db.commit()
    db.refresh(rec)
    return rec

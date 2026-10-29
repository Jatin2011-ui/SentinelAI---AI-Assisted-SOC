
"""Event normalization utilities."""
from datetime import datetime, timezone

from app.models.event import SecurityEvent
from app.schemas.events import EventIngest


def normalize_event(ingest: EventIngest, raw_payload: dict | None = None) -> SecurityEvent:
    # Ensure timestamp is timezone aware
    ts = ingest.timestamp
    if ts.tzinfo is None:
        ts = ts.replace(tzinfo=timezone.utc)

    # Build normalized SecurityEvent instance
    event = SecurityEvent(
        timestamp=ts,
        source=ingest.source or "unknown",
        event_type=ingest.event_type,
        source_ip=ingest.source_ip,
        destination_ip=ingest.destination_ip,
        source_port=ingest.source_port,
        destination_port=ingest.destination_port,
        protocol=ingest.protocol,
        username=ingest.username,
        hostname=ingest.hostname,
        process_name=ingest.process_name,
        command=ingest.command,
        file_path=ingest.file_path,
        severity=ingest.severity or "LOW",
        raw_message=ingest.raw_message or "",
        raw=raw_payload or ingest.model_dump(mode="json"),
        extra=ingest.extra or {},
    )
    return event

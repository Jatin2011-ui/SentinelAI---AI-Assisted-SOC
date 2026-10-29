"""Normalized security event (PRD section 8)."""
from app.models.common import *  # noqa: F401,F403


class SecurityEvent(Base):
    __tablename__ = "security_events"

    event_id: Mapped[str] = mapped_column(String(36), primary_key=True, default=new_uuid)
    timestamp: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, index=True)
    source: Mapped[str] = mapped_column(String(128), default="unknown")
    event_type: Mapped[str] = mapped_column(String(64), nullable=False, index=True)

    source_ip: Mapped[str | None] = mapped_column(String(64), nullable=True, index=True)
    destination_ip: Mapped[str | None] = mapped_column(String(64), nullable=True, index=True)
    source_port: Mapped[int | None] = mapped_column(nullable=True)
    destination_port: Mapped[int | None] = mapped_column(nullable=True)
    protocol: Mapped[str | None] = mapped_column(String(32), nullable=True)

    username: Mapped[str | None] = mapped_column(String(255), nullable=True, index=True)
    hostname: Mapped[str | None] = mapped_column(String(255), nullable=True, index=True)
    process_name: Mapped[str | None] = mapped_column(String(255), nullable=True)
    command: Mapped[str | None] = mapped_column(Text, nullable=True)
    file_path: Mapped[str | None] = mapped_column(Text, nullable=True)

    severity: Mapped[str] = mapped_column(String(16), default=Severity.LOW.value)
    raw_message: Mapped[str] = mapped_column(Text, default="")
    raw: Mapped[dict] = mapped_column(JSON, default=dict)  # preserved original payload
    extra: Mapped[dict] = mapped_column("metadata", JSON, default=dict)

    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow)


class FeatureRecord(Base):
    """Stored ML feature vectors so decisions are reproducible (PRD section 9)."""

    __tablename__ = "features"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=new_uuid)
    event_id: Mapped[str | None] = mapped_column(ForeignKey("security_events.event_id"), nullable=True, index=True)
    subject_type: Mapped[str] = mapped_column(String(32), default="event")  # event | window | incident
    subject_key: Mapped[str] = mapped_column(String(255), default="")
    feature_version: Mapped[str] = mapped_column(String(64), nullable=False)
    vector: Mapped[dict] = mapped_column(JSON, default=dict)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow)

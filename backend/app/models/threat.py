"""Threat intelligence cache and MITRE ATT&CK reference (PRD sections 18-19)."""
from app.models.common import *  # noqa: F401,F403


class ThreatIntelligence(Base):
    __tablename__ = "threat_intelligence"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=new_uuid)
    indicator_id: Mapped[str] = mapped_column(ForeignKey("indicators.id"), nullable=False, index=True)
    provider: Mapped[str] = mapped_column(String(64), nullable=False)
    verdict: Mapped[str] = mapped_column(String(32), default="unknown")  # benign/suspicious/malicious/unknown
    score: Mapped[float] = mapped_column(default=0.0)  # 0..1, higher = more malicious
    raw: Mapped[dict] = mapped_column(JSON, default=dict)
    fetched_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow)


class MitreTechnique(Base):
    __tablename__ = "mitre_techniques"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=new_uuid)
    technique_id: Mapped[str] = mapped_column(String(16), unique=True, nullable=False, index=True)  # e.g. T1110
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    tactic: Mapped[str] = mapped_column(String(128), default="")
    description: Mapped[str] = mapped_column(Text, default="")

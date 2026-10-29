"""Shared imports/helpers for model modules."""
import uuid
from datetime import datetime, timezone

from sqlalchemy import JSON, Boolean, DateTime, ForeignKey, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base
from app.models.enums import (
    ActionStatus,
    AgentRunStatus,
    ApprovalDecision,
    AttackClass,
    IncidentStatus,
    IndicatorType,
    RoleName,
    Severity,
)


def new_uuid() -> str:
    return str(uuid.uuid4())


def utcnow() -> datetime:
    return datetime.now(timezone.utc)


__all__ = [
    "Base", "Mapped", "mapped_column", "relationship",
    "String", "Text", "Integer", "DateTime", "ForeignKey", "JSON", "Boolean",
    "datetime", "new_uuid", "utcnow",
    "ActionStatus", "AgentRunStatus", "ApprovalDecision", "AttackClass",
    "IncidentStatus", "IndicatorType", "RoleName", "Severity",
]

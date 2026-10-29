"""Event schemas for ingestion and response."""
from datetime import datetime
from typing import Any, Optional

from pydantic import BaseModel, ConfigDict, Field


class EventIngest(BaseModel):
    timestamp: datetime = Field(..., description="Event timestamp in ISO8601")
    source: Optional[str] = Field(default="unknown", max_length=128)
    event_type: str = Field(..., max_length=64)
    source_ip: Optional[str] = Field(default=None, max_length=64)
    destination_ip: Optional[str] = Field(default=None, max_length=64)
    source_port: Optional[int] = Field(default=None)
    destination_port: Optional[int] = Field(default=None)
    protocol: Optional[str] = Field(default=None, max_length=32)
    username: Optional[str] = Field(default=None, max_length=255)
    hostname: Optional[str] = Field(default=None, max_length=255)
    process_name: Optional[str] = Field(default=None, max_length=255)
    command: Optional[str] = None
    file_path: Optional[str] = None
    severity: Optional[str] = Field(default="LOW", max_length=16)
    raw_message: Optional[str] = Field(default="")
    extra: Optional[dict[str, Any]] = Field(default_factory=dict)


class EventResponse(BaseModel):
    event_id: str
    timestamp: datetime
    source: str
    event_type: str
    source_ip: Optional[str]
    destination_ip: Optional[str]
    severity: str

    model_config = ConfigDict(from_attributes=True)

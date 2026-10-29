
"""SOC agent state model."""
from typing import Any, Dict, List, Optional

from pydantic import BaseModel


class SOCState(BaseModel):
    incident_id: str
    incident: Optional[Dict[str, Any]] = None
    events: List[Dict[str, Any]] = []
    evidence: List[Dict[str, Any]] = []
    threat_intelligence: Dict[str, Any] = {}
    mitre_mapping: List[Dict[str, Any]] = []
    hypotheses: List[Dict[str, Any]] = []
    risk_score: float = 0.0
    recommended_actions: List[Dict[str, Any]] = []
    approval_status: Optional[str] = None
    investigation_history: List[str] = []

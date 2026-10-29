"""Enumerations shared across models (stored as strings for portability)."""
from enum import StrEnum


class RoleName(StrEnum):
    ADMIN = "ADMIN"
    SOC_ANALYST = "SOC_ANALYST"
    VIEWER = "VIEWER"


class IncidentStatus(StrEnum):
    NEW = "NEW"
    INVESTIGATING = "INVESTIGATING"
    CONTAINED = "CONTAINED"
    RESOLVED = "RESOLVED"
    FALSE_POSITIVE = "FALSE_POSITIVE"
    REOPENED = "REOPENED"


class Severity(StrEnum):
    LOW = "LOW"
    MEDIUM = "MEDIUM"
    HIGH = "HIGH"
    CRITICAL = "CRITICAL"


class AttackClass(StrEnum):
    BENIGN = "BENIGN"
    BRUTE_FORCE = "BRUTE_FORCE"
    CREDENTIAL_ATTACK = "CREDENTIAL_ATTACK"
    PORT_SCAN = "PORT_SCAN"
    MALWARE = "MALWARE"
    SUSPICIOUS_PROCESS = "SUSPICIOUS_PROCESS"
    PRIVILEGE_ESCALATION = "PRIVILEGE_ESCALATION"
    DATA_EXFILTRATION = "DATA_EXFILTRATION"
    OTHER = "OTHER"


class ActionStatus(StrEnum):
    PROPOSED = "PROPOSED"
    WAITING_FOR_APPROVAL = "WAITING_FOR_APPROVAL"
    APPROVED = "APPROVED"
    REJECTED = "REJECTED"
    EXECUTED = "EXECUTED"
    FAILED = "FAILED"
    SIMULATED = "SIMULATED"


class ApprovalDecision(StrEnum):
    APPROVED = "APPROVED"
    REJECTED = "REJECTED"


class AgentRunStatus(StrEnum):
    PENDING = "PENDING"
    RUNNING = "RUNNING"
    COMPLETED = "COMPLETED"
    FAILED = "FAILED"
    WAITING_FOR_APPROVAL = "WAITING_FOR_APPROVAL"


class IndicatorType(StrEnum):
    IP = "ip"
    DOMAIN = "domain"
    URL = "url"
    HASH = "hash"
    CVE = "cve"

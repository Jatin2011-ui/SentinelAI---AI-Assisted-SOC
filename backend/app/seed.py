"""Seed roles, admin user, MITRE reference rows, and default settings.

Idempotent: safe to run on every container start.
"""
from sqlalchemy import select

from app.core.config import get_settings
from app.core.logging import get_logger
from app.core.security import hash_password
from app.db.session import SessionLocal
from app.models.enums import RoleName
from app.models.system import SystemSetting
from app.models.threat import MitreTechnique
from app.models.user import Role, User

log = get_logger("seed")

ROLE_PERMISSIONS: dict[str, list[str]] = {
    RoleName.ADMIN.value: ["*"],
    RoleName.SOC_ANALYST.value: [
        "events:read", "incidents:read", "incidents:investigate",
        "approvals:decide", "threat_intel:read", "audit:read",
    ],
    RoleName.VIEWER.value: ["events:read", "incidents:read"],
}

# Small reference subset; full ATT&CK import comes with Phase 5.
MITRE_SEED = [
    ("T1110", "Brute Force", "Credential Access", "Adversaries may use brute force to gain access."),
    ("T1078", "Valid Accounts", "Defense Evasion", "Adversaries may use valid accounts to maintain access."),
    ("T1068", "Exploitation for Privilege Escalation", "Privilege Escalation", "Adversaries may exploit software vulnerabilities to elevate privileges."),
    ("T1059", "Command and Scripting Interpreter", "Execution", "Adversaries may abuse command interpreters to execute commands."),
    ("T1046", "Network Service Discovery", "Discovery", "Adversaries may attempt to get a listing of services running on remote hosts (port scanning)."),
    ("T1041", "Exfiltration Over C2 Channel", "Exfiltration", "Adversaries may steal data by exfiltrating it over a command and control channel."),
]

DEFAULT_SETTINGS = {
    "risk_engine": {
        "weights": {
            "threat_severity": 30,
            "ml_confidence": 20,
            "asset_criticality": 15,
            "evidence_strength": 15,
            "threat_intel": 10,
            "behavioral_anomaly": 10,
        },
        "bands": {"LOW": [0, 25], "MEDIUM": [26, 50], "HIGH": [51, 75], "CRITICAL": [76, 100]},
    },
    "response_policy": {
        "LOW": "auto",
        "MEDIUM": "policy",   # decided per-action risk class
        "HIGH": "approval",
        "CRITICAL": "approval_with_verification",
    },
    "detection": {"anomaly_threshold": 0.6, "classification_threshold": 0.5},
}


def seed() -> None:
    settings = get_settings()
    db = SessionLocal()
    try:
        roles: dict[str, Role] = {}
        for name, perms in ROLE_PERMISSIONS.items():
            role = db.scalar(select(Role).where(Role.name == name))
            if role is None:
                role = Role(name=name, permissions=perms)
                db.add(role)
                db.flush()
                log.info("role_created", role=name)
            roles[name] = role

        admin = db.scalar(select(User).where(User.email == settings.seed_admin_email))
        if admin is None:
            db.add(User(
                email=settings.seed_admin_email,
                full_name="Sentinel Admin",
                password_hash=hash_password(settings.seed_admin_password),
                role_id=roles[RoleName.ADMIN.value].id,
            ))
            log.info("admin_seeded", email=settings.seed_admin_email)

        for tid, name, tactic, desc in MITRE_SEED:
            if db.scalar(select(MitreTechnique).where(MitreTechnique.technique_id == tid)) is None:
                db.add(MitreTechnique(technique_id=tid, name=name, tactic=tactic, description=desc))

        for key, value in DEFAULT_SETTINGS.items():
            if db.scalar(select(SystemSetting).where(SystemSetting.key == key)) is None:
                db.add(SystemSetting(key=key, value=value))

        db.commit()
        log.info("seed_complete")
    finally:
        db.close()


if __name__ == "__main__":
    seed()

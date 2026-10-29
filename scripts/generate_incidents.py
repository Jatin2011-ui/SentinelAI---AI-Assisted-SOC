"""
Targeted incident seed script.

Injects realistic attack-scenario event clusters so that the correlator
creates meaningful incidents immediately.

Scenarios:
  1. Brute-force SSH (5 auth failures + 1 success) - HIGH
  2. Lateral movement from a compromised host (6 events, same user/host) - MEDIUM
  3. Data exfiltration attempt (5 network + 1 DNS, same IP) - MEDIUM
  4. Privileged account abuse (5 events, admin user) - MEDIUM
  5. Ransomware-like file activity (7 file_modification + suspicious_command_execution) - MEDIUM
"""
import sys
import os
from datetime import datetime, timedelta, timezone

# ── Path / env bootstrap (must happen BEFORE any app imports) ──────────────
SCRIPT_DIR   = os.path.dirname(os.path.abspath(__file__))
BACKEND_DIR  = os.path.normpath(os.path.join(SCRIPT_DIR, "..", "backend"))
DB_PATH      = os.path.join(BACKEND_DIR, "sentinel_dev.db")

# Set DATABASE_URL so app.core.config picks it up
os.environ.setdefault("DATABASE_URL", f"sqlite:///{DB_PATH}")
os.environ.setdefault("JWT_SECRET", "devsecret")

# Make sure 'app' package is importable
if BACKEND_DIR not in sys.path:
    sys.path.insert(0, BACKEND_DIR)

from app.db.session import SessionLocal  # noqa: E402
from app.models.event import SecurityEvent  # noqa: E402

NOW = datetime.now(timezone.utc)

def _m(m: int) -> datetime:
    return NOW - timedelta(minutes=m)

SCENARIOS: list[dict] = []

# ── 1. Brute-force SSH ─────────────────────────────────────────────────────
for i in range(6):
    SCENARIOS.append(dict(
        timestamp=_m(15 - i), source="auth-server",
        event_type="authentication_failure",
        source_ip="10.0.0.66", destination_ip="192.168.1.20",
        destination_port=22, protocol="SSH",
        username="svc_admin", hostname="server-01", severity="HIGH",
        raw_message=f"Failed password for svc_admin from 10.0.0.66 port {50000+i} ssh2",
    ))
SCENARIOS.append(dict(
    timestamp=_m(8), source="auth-server",
    event_type="authentication_success",
    source_ip="10.0.0.66", destination_ip="192.168.1.20",
    destination_port=22, protocol="SSH",
    username="svc_admin", hostname="server-01", severity="CRITICAL",
    raw_message="Accepted password for svc_admin from 10.0.0.66 after 6 failures",
))

# ── 2. Lateral movement ────────────────────────────────────────────────────
for i, t in enumerate([
    "network_connection", "authentication_failure", "authentication_success",
    "process_creation", "file_modification", "network_connection",
]):
    SCENARIOS.append(dict(
        timestamp=_m(60 - i * 5), source="endpoint", event_type=t,
        source_ip="192.168.10.55", destination_ip=f"192.168.10.{100+i}",
        destination_port=445, protocol="SMB",
        username="jdoe", hostname="ws-infected", severity="MEDIUM",
        raw_message=f"Lateral movement step {i+1}: {t}",
    ))

# ── 3. Data exfiltration ───────────────────────────────────────────────────
for i in range(4):
    SCENARIOS.append(dict(
        timestamp=_m(30 - i * 4), source="firewall",
        event_type="network_connection",
        source_ip="192.168.1.99", destination_ip="185.220.101.47",
        destination_port=443, protocol="HTTPS",
        username=None, hostname="db-server-02", severity="HIGH",
        raw_message=f"Large outbound transfer #{i+1} to suspicious external IP",
    ))
SCENARIOS.append(dict(
    timestamp=_m(10), source="dns", event_type="dns_request",
    source_ip="192.168.1.99", destination_ip="8.8.8.8",
    destination_port=53, protocol="UDP",
    username=None, hostname="db-server-02", severity="MEDIUM",
    raw_message="DNS request to suspicious domain exfil.attacker.io",
))

# ── 4. Privileged account abuse ────────────────────────────────────────────
for i, (t, p) in enumerate([
    ("authentication_success", 3389), ("process_creation", 445),
    ("suspicious_command_execution", 445), ("file_modification", 445),
    ("network_connection", 8080),
]):
    SCENARIOS.append(dict(
        timestamp=_m(120 - i * 10), source="endpoint", event_type=t,
        source_ip="172.16.5.10", destination_ip="10.10.0.1",
        destination_port=p, protocol="TCP",
        username="administrator", hostname="jump-host", severity="HIGH",
        raw_message=f"Admin abuse event: {t}",
    ))

# ── 5. Ransomware-like file activity ───────────────────────────────────────
for i in range(6):
    SCENARIOS.append(dict(
        timestamp=_m(45 - i * 3), source="endpoint",
        event_type="file_modification",
        source_ip="192.168.2.77", destination_ip="192.168.2.77",
        destination_port=0, protocol="LOCAL",
        username="bob.smith", hostname="workstation-14", severity="HIGH",
        raw_message=f"Mass file rename/encrypt #{i+1}: documents.{i+1}.locked",
    ))
SCENARIOS.append(dict(
    timestamp=_m(20), source="endpoint",
    event_type="suspicious_command_execution",
    source_ip="192.168.2.77", destination_ip="192.168.2.77",
    destination_port=0, protocol="LOCAL",
    username="bob.smith", hostname="workstation-14", severity="CRITICAL",
    raw_message="cmd.exe /c vssadmin delete shadows /all /quiet",
))


def insert_scenarios() -> None:
    db = SessionLocal()
    try:
        for data in SCENARIOS:
            ev = SecurityEvent(
                timestamp=data["timestamp"],
                source=data["source"],
                event_type=data["event_type"],
                source_ip=data.get("source_ip"),
                destination_ip=data.get("destination_ip"),
                source_port=None,
                destination_port=data.get("destination_port"),
                protocol=data.get("protocol"),
                username=data.get("username"),
                hostname=data.get("hostname"),
                severity=data["severity"],
                raw_message=data["raw_message"],
                raw={"scenario": True},
                extra={},
            )
            db.add(ev)
        db.commit()
        print(f"Inserted {len(SCENARIOS)} scenario events across 5 attack clusters.")
        print(f"    DB: {DB_PATH}")
    finally:
        db.close()


if __name__ == "__main__":
    print(f"Using DATABASE_URL: {os.environ['DATABASE_URL']}")
    insert_scenarios()

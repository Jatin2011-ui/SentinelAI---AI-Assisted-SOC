"""Synthetic security event generator for demo purposes."""
import random
from datetime import datetime, timedelta, timezone

from app.db.session import SessionLocal
from app.models.event import SecurityEvent

EVENT_TYPES = [
    "authentication_failure",
    "authentication_success",
    "process_creation",
    "file_modification",
    "network_connection",
    "dns_request",
    "suspicious_command_execution",
]

def generate_events(count: int = 50):
    # Use existing SessionLocal; for demo we assume DB is accessible
    db = SessionLocal()
    base = datetime.now(timezone.utc) - timedelta(hours=24)
    for i in range(count):
        ts = base + timedelta(minutes=random.randint(0, 1440))
        ev = SecurityEvent(
            timestamp=ts,
            source=random.choice(["firewall", "endpoint", "ids", "auth-server"]),
            event_type=random.choice(EVENT_TYPES),
            source_ip=f"192.168.1.{random.randint(1, 254)}",
            destination_ip=f"10.0.0.{random.randint(1, 254)}",
            source_port=random.randint(1024, 65535),
            destination_port=random.choice([22, 80, 443, 3389]),
            protocol=random.choice(["TCP", "UDP", "SSH"]),
            username=random.choice(["admin", "svc_account", "john.doe", None]),
            hostname=f"host-{random.randint(1, 20):02d}",
            severity=random.choice(["LOW", "MEDIUM", "HIGH"]),
            raw_message="Synthetic event for demo",
            raw={"synthetic": True, "index": i},
            extra={},
        )
        db.add(ev)
    db.commit()
    db.close()
    print(f"Generated {count} synthetic events.")

if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("--count", type=int, default=50)
    args = parser.parse_args()
    generate_events(args.count)

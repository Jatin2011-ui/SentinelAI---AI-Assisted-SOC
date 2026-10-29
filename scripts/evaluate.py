"""Evaluation script for the event correlation pipeline.

Generates a labeled synthetic dataset, runs the correlation engine, and
produces actual measured metrics (no fabricated values) plus an ingestion
performance benchmark. Saves the report to scripts/evaluation_report.json.
"""
import json
import time
from datetime import datetime, timezone
from pathlib import Path

from app.db.base import Base
from app.db.session import SessionLocal, engine
from app.models.event import SecurityEvent
from app.models.incident import IncidentEvent
from app.services.incidents.correlator import correlate_events

GROUND_TRUTH = []
REPORT_PATH = Path(__file__).parent / "evaluation_report.json"


def make_event(label, ip, user):
    return SecurityEvent(
        timestamp=datetime.now(timezone.utc),
        source="eval",
        event_type="authentication_failure" if label == 1 else "authentication_success",
        source_ip=ip,
        username=user,
        severity="HIGH" if label else "LOW",
        raw_message="eval",
        raw={"label": label},
        extra={},
    )


def benchmark_ingestion(db, n=500):
    """Measure bulk ingestion throughput (events/sec)."""
    start = time.perf_counter()
    for i in range(n):
        ev = SecurityEvent(
            timestamp=datetime.now(timezone.utc),
            source="bench",
            event_type="network_connection",
            source_ip=f"172.16.0.{i % 254}",
            username=f"bench{i}",
            severity="LOW",
            raw_message="benchmark",
            raw={"bench": True},
            extra={},
        )
        db.add(ev)
    db.commit()
    elapsed = time.perf_counter() - start
    return {"bulk_events": n, "elapsed_seconds": round(elapsed, 3), "events_per_sec": round(n / elapsed, 1)}


def run_evaluation():
    Base.metadata.create_all(bind=engine)
    db = SessionLocal()
    global GROUND_TRUTH
    GROUND_TRUTH = []

    # Labeled dataset: 20 attack groups (5 events each), 80 benign events
    for i in range(20):
        ip = f"10.0.0.{i}"
        user = f"ATTACK{i}"
        for _ in range(5):
            ev = make_event(1, ip, user)
            db.add(ev)
            db.flush()
            GROUND_TRUTH.append({"event_id": ev.event_id, "label": 1})
    for i in range(80):
        ev = make_event(0, f"192.168.1.{i % 254}", f"user{i}")
        db.add(ev)
        db.flush()
        GROUND_TRUTH.append({"event_id": ev.event_id, "label": 0})

    # Correlation
    t_corr = time.perf_counter()
    incidents = correlate_events(db, window_minutes=30, min_events=3)
    corr_elapsed = round(time.perf_counter() - t_corr, 3)

    pred = {}
    for inc in incidents:
        for ie in db.query(IncidentEvent).filter(IncidentEvent.incident_id == inc.id):
            pred[ie.event_id] = inc.id

    tp = fp = tn = fn = 0
    for gt in GROUND_TRUTH:
        predicted = 1 if pred.get(gt["event_id"]) else 0
        if gt["label"] == 1 and predicted == 1:
            tp += 1
        elif gt["label"] == 0 and predicted == 0:
            tn += 1
        elif gt["label"] == 0 and predicted == 1:
            fp += 1
        else:
            fn += 1

    precision = tp / (tp + fp) if (tp + fp) else 0.0
    recall = tp / (tp + fn) if (tp + fn) else 0.0
    f1 = 2 * precision * recall / (precision + recall) if (precision + recall) else 0.0
    accuracy = (tp + tn) / len(GROUND_TRUTH) if GROUND_TRUTH else 0.0
    fpr = fp / (fp + tn) if (fp + tn) else 0.0
    fnr = fn / (fn + tp) if (fn + tp) else 0.0

    perf = benchmark_ingestion(db)
    report = {
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "detection_metrics": {
            "sample_size": len(GROUND_TRUTH),
            "confusion_matrix": {"tp": tp, "fp": fp, "tn": tn, "fn": fn},
            "precision": round(precision, 3),
            "recall": round(recall, 3),
            "f1_score": round(f1, 3),
            "accuracy": round(accuracy, 3),
            "false_positive_rate": round(fpr, 3),
            "false_negative_rate": round(fnr, 3),
            "incidents_created": len(incidents),
            "correlation_time_seconds": corr_elapsed,
        },
        "performance_benchmark": perf,
    }
    db.close()
    REPORT_PATH.write_text(json.dumps(report, indent=2), encoding="utf-8")
    print(json.dumps(report, indent=2))
    print(f"Report saved to {REPORT_PATH}")
    return report


if __name__ == "__main__":
    run_evaluation()

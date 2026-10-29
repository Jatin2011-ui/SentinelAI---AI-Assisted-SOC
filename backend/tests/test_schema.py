"""Verify the full PRD section-30 schema exists."""
from sqlalchemy import inspect

from tests.conftest import engine

EXPECTED_TABLES = {
    # PRD section 30 required tables
    "users", "roles", "security_events", "incidents", "incident_events",
    "indicators", "threat_intelligence", "mitre_techniques", "ml_predictions",
    "agent_runs", "agent_messages", "response_actions", "approvals",
    "audit_logs", "model_versions", "system_settings",
    # additions decided during planning
    "features", "ml_models", "refresh_tokens",
}


def test_all_required_tables_exist():
    existing = set(inspect(engine).get_table_names())
    missing = EXPECTED_TABLES - existing
    assert not missing, f"Missing tables: {missing}"


def test_security_event_columns():
    cols = {c["name"] for c in inspect(engine).get_columns("security_events")}
    required = {
        "event_id", "timestamp", "source", "event_type", "source_ip",
        "destination_ip", "source_port", "destination_port", "protocol",
        "username", "hostname", "process_name", "command", "file_path",
        "severity", "raw_message", "metadata",
    }
    assert required <= cols


def test_incident_columns():
    cols = {c["name"] for c in inspect(engine).get_columns("incidents")}
    required = {
        "id", "title", "description", "severity", "risk_score", "confidence",
        "status", "created_at", "updated_at", "affected_assets", "indicators",
        "mitre_techniques", "ai_summary", "recommended_actions",
        "approved_actions", "investigation_history",
    }
    assert required <= cols

"""initial schema: users, roles, refresh_tokens, security_events, features,
incidents, incident_events, indicators, threat_intelligence, mitre_techniques,
ml_models, model_versions, ml_predictions, agent_runs, agent_messages,
response_actions, approvals, audit_logs, system_settings

Revision ID: 0001_initial
Revises:
Create Date: 2026-09-05
"""
from alembic import op

from app.db.base import Base

revision = "0001_initial"
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    Base.metadata.create_all(bind=op.get_bind())


def downgrade() -> None:
    Base.metadata.drop_all(bind=op.get_bind())

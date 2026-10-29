"""Import all ORM models so SQLAlchemy metadata is fully registered."""
from app.models import (  # noqa: F401
    agent,
    audit,
    event,
    incident,
    ml,
    system,
    threat,
    user,
)

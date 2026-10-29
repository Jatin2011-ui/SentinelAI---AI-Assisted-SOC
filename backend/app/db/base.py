"""SQLAlchemy declarative base.

Only defines Base. Model modules are registered for metadata by importing
``app.models`` (see ``app/models/__init__.py`` and ``alembic/env.py``).
"""
from sqlalchemy.orm import DeclarativeBase


class Base(DeclarativeBase):
    pass

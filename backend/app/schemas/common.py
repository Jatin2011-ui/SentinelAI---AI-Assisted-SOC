"""Shared schema primitives."""
import re
from typing import Annotated

from pydantic import AfterValidator

# Permissive RFC-5322-ish check. Deliberately does not reject reserved TLDs
# (e.g. .local, .internal) because SentinelAI commonly runs in lab/demo setups
# with addresses like admin@sentinel.local.
_EMAIL_RE = re.compile(r"^[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,63}$")


def _validate_email(value: str) -> str:
    if not _EMAIL_RE.match(value):
        raise ValueError("invalid email address")
    return value.strip().lower()


EmailAddress = Annotated[str, AfterValidator(_validate_email)]

__all__ = ["EmailAddress"]

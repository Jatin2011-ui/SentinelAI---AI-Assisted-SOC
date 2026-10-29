"""FastAPI dependencies: current user extraction and RBAC guards."""
import jwt
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy.orm import Session

from app.core.security import decode_token
from app.db.session import get_db
from app.models.enums import RoleName
from app.models.user import User

bearer = HTTPBearer(auto_error=True)

_ROLE_RANK = {RoleName.VIEWER: 0, RoleName.SOC_ANALYST: 1, RoleName.ADMIN: 2}


def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(bearer),
    db: Session = Depends(get_db),
) -> User:
    try:
        payload = decode_token(credentials.credentials)
    except jwt.PyJWTError:
        raise HTTPException(status.HTTP_401_UNAUTHORIZED, "Invalid or expired token")
    if payload.get("type") != "access":
        raise HTTPException(status.HTTP_401_UNAUTHORIZED, "Wrong token type")
    user = db.get(User, payload["sub"])
    if user is None or not user.is_active:
        raise HTTPException(status.HTTP_401_UNAUTHORIZED, "User not found or inactive")
    return user


def require_roles(*roles: RoleName):
    allowed = {RoleName(r) for r in roles}

    def checker(user: User = Depends(get_current_user)) -> User:
        if RoleName(user.role.name) not in allowed:
            raise HTTPException(status.HTTP_403_FORBIDDEN, "Insufficient permissions")
        return user

    return checker


require_admin = require_roles(RoleName.ADMIN)
require_analyst = require_roles(RoleName.ADMIN, RoleName.SOC_ANALYST)

__all__ = ["get_db", "get_current_user", "require_roles", "require_admin", "require_analyst"]

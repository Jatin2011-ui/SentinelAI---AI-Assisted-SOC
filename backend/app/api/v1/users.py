"""Admin user management (PRD section 41)."""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.api.deps import get_db, require_admin
from app.core.security import hash_password
from app.models.enums import RoleName
from app.models.user import Role, User
from app.schemas.auth import UserCreate, UserOut

router = APIRouter(prefix="/users", tags=["users"], dependencies=[Depends(require_admin)])


def _to_out(u: User) -> UserOut:
    return UserOut(id=u.id, email=u.email, full_name=u.full_name, role=u.role.name, is_active=u.is_active)


@router.get("", response_model=list[UserOut])
def list_users(db: Session = Depends(get_db)) -> list[UserOut]:
    return [_to_out(u) for u in db.scalars(select(User)).all()]


@router.post("", response_model=UserOut, status_code=status.HTTP_201_CREATED)
def create_user(body: UserCreate, db: Session = Depends(get_db)) -> UserOut:
    if db.scalar(select(User).where(User.email == body.email)):
        raise HTTPException(status.HTTP_409_CONFLICT, "Email already registered")
    try:
        role_name = RoleName(body.role)
    except ValueError:
        raise HTTPException(status.HTTP_422_UNPROCESSABLE_ENTITY, f"Unknown role: {body.role}")
    role = db.scalar(select(Role).where(Role.name == role_name.value))
    if role is None:
        role = Role(name=role_name.value, permissions=[])
        db.add(role)
        db.flush()
    user = User(
        email=body.email,
        full_name=body.full_name,
        password_hash=hash_password(body.password),
        role_id=role.id,
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return _to_out(user)

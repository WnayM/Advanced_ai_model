from __future__ import annotations
from sqlalchemy.orm import Session
from infr.postgres.models import User


def get_user_by_external_id(db: Session, external_id: str) -> User | None:
    return db.query(User).filter(User.external_id == external_id).one_or_none()


def get_or_create_user(db: Session, external_id: str) -> User:
    u = get_user_by_external_id(db, external_id)
    if u:
        return u
    u = User(external_id=external_id)
    db.add(u)
    db.commit()
    db.refresh(u)
    return u

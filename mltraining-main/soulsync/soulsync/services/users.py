from __future__ import annotations
from datetime import datetime
from sqlalchemy.orm import Session
from soulsync.models import User, Profile, Stat, STAT_TYPES

def get_user(db: Session, user_id: int) -> User:
    return db.query(User).filter(User.id == user_id).one()

def ensure_profile(db: Session, user_id: int) -> Profile:
    prof = db.query(Profile).filter(Profile.user_id == user_id).one_or_none()
    if prof is None:
        prof = Profile(user_id=user_id, timezone="UTC", streak_count=0, last_login_at=datetime.utcnow())
        db.add(prof)
        db.flush()
    return prof

def ensure_all_stats(db: Session, user_id: int) -> None:
    existing = {s.type for s in db.query(Stat).filter(Stat.user_id == user_id).all()}
    for t in STAT_TYPES:
        if t not in existing:
            db.add(Stat(user_id=user_id, type=t, level=1, xp=0))
    db.flush()

def is_onboarded(profile: Profile) -> bool:
    return bool(profile.goals_json and profile.timezone)

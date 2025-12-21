from __future__ import annotations

from datetime import datetime
from sqlalchemy.orm import Session

from soulsync.models import (
    User, Profile, Stat,
    MissionAssignment,
    JournalEntry, VoiceMessage, VoiceMemory,
    RankSnapshot, AuditLog
)


def delete_voice_history(db: Session, user_id: int) -> int:
    """Delete VoiceMessage rows for user. Returns count deleted."""
    q = db.query(VoiceMessage).filter(VoiceMessage.user_id == user_id)
    count = q.count()
    q.delete(synchronize_session=False)
    db.flush()
    db.add(AuditLog(user_id=user_id, event_type="voice_history_deleted", meta_json=None, created_at=datetime.utcnow()))
    db.flush()
    return count


def delete_voice_memory(db: Session, user_id: int) -> int:
    """Delete VoiceMemory rows for user. Returns count deleted."""
    q = db.query(VoiceMemory).filter(VoiceMemory.user_id == user_id)
    count = q.count()
    q.delete(synchronize_session=False)
    db.flush()
    db.add(AuditLog(user_id=user_id, event_type="voice_memory_deleted", meta_json=None, created_at=datetime.utcnow()))
    db.flush()
    return count


def delete_account(db: Session, user_id: int) -> None:
    """Full wipe of user-related data."""
    db.query(RankSnapshot).filter(RankSnapshot.user_id == user_id).delete(synchronize_session=False)

    db.query(MissionAssignment).filter(MissionAssignment.user_id == user_id).delete(synchronize_session=False)
    db.query(JournalEntry).filter(JournalEntry.user_id == user_id).delete(synchronize_session=False)
    db.query(VoiceMessage).filter(VoiceMessage.user_id == user_id).delete(synchronize_session=False)
    db.query(VoiceMemory).filter(VoiceMemory.user_id == user_id).delete(synchronize_session=False)

    db.query(Stat).filter(Stat.user_id == user_id).delete(synchronize_session=False)
    db.query(Profile).filter(Profile.user_id == user_id).delete(synchronize_session=False)

    db.query(AuditLog).filter(AuditLog.user_id == user_id).delete(synchronize_session=False)

    u = db.query(User).filter(User.id == user_id).one_or_none()
    if u:
        db.delete(u)

    db.flush()

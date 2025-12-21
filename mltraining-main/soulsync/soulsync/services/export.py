from __future__ import annotations

import json
from datetime import datetime
from sqlalchemy.orm import Session

from soulsync.models import (
    User, Profile, Stat,
    Mission, MissionAssignment,
    JournalEntry, VoiceMemory
)


def _dt(x):
    if not x:
        return None
    if isinstance(x, datetime):
        return x.isoformat()
    return str(x)


def export_user_data_minimal(db: Session, user_id: int) -> dict:
    """Minimal export (default): profile, stats, missions/assignments, journal, voice_memory.

    Excludes by default:
    - VoiceMessage chat history
    - AuditLog
    """
    user = db.query(User).filter(User.id == user_id).one()

    profile = db.query(Profile).filter(Profile.user_id == user_id).one_or_none()
    stats = db.query(Stat).filter(Stat.user_id == user_id).all()

    assignments = (
        db.query(MissionAssignment, Mission)
        .join(Mission, Mission.id == MissionAssignment.mission_id)
        .filter(MissionAssignment.user_id == user_id)
        .order_by(MissionAssignment.date.asc())
        .all()
    )

    journal = (
        db.query(JournalEntry)
        .filter(JournalEntry.user_id == user_id)
        .order_by(JournalEntry.created_at.asc())
        .all()
    )

    voice_memory = (
        db.query(VoiceMemory)
        .filter(VoiceMemory.user_id == user_id)
        .order_by(VoiceMemory.created_at.asc())
        .all()
    )

    out = {
        "exported_at": datetime.utcnow().isoformat(),
        "user": {
            "id": user.id,
            "email": user.email,
            "handle": user.handle,
            "consent_leaderboard": user.consent_leaderboard,
            "consent_location": user.consent_location,
            "city": user.city,
            "region": user.region,
            "created_at": _dt(user.created_at),
        },
        "profile": None if not profile else {
            "avatar_url": profile.avatar_url,
            "goals_json": profile.goals_json,
            "timezone": profile.timezone,
            "streak_count": profile.streak_count,
            "last_login_at": _dt(profile.last_login_at),
        },
        "stats": [
            {
                "type": s.type,
                "level": s.level,
                "xp": s.xp,
                "updated_at": _dt(s.updated_at),
            } for s in stats
        ],
        "missions": [
            {
                "assignment": {
                    "id": a.id,
                    "date": str(a.date),
                    "status": a.status,
                    "proof_json": a.proof_json,
                    "completed_at": _dt(a.completed_at),
                },
                "mission": {
                    "id": m.id,
                    "title": m.title,
                    "type": m.type,
                    "difficulty": m.difficulty,
                    "xp_reward": m.xp_reward,
                    "is_hidden": m.is_hidden,
                    # No user coordinates are stored; include rule only as stored in mission.
                    "geo_rule_json": m.geo_rule_json if m.is_hidden else None,
                    "created_for_date": str(m.created_for_date),
                    "created_by_system": m.created_by_system,
                }
            } for (a, m) in assignments
        ],
        "journal": [
            {
                "id": j.id,
                "mood": j.mood,
                "text": j.text,
                "tags": j.tags,
                "created_at": _dt(j.created_at),
            } for j in journal
        ],
        "voice_memory": [
            {
                "id": vm.id,
                "kind": vm.kind,
                "content": vm.content,
                "created_at": _dt(vm.created_at),
                "updated_at": _dt(vm.updated_at),
                "has_vector": bool(vm.vector),
            } for vm in voice_memory
        ],
    }

    return out


def export_user_json_bytes(db: Session, user_id: int) -> bytes:
    data = export_user_data_minimal(db, user_id)
    return json.dumps(data, ensure_ascii=False, indent=2).encode("utf-8")

from __future__ import annotations

import json
import random
from datetime import datetime, timedelta
from sqlalchemy.orm import Session

from soulsync.models import Mission, MissionAssignment, Profile, AuditLog
from soulsync.services.stats import grant_stat_xp
from soulsync.services.timeutil import today_in_tz

MISSION_CATALOG = [
    ("📚 Study sprint: 20 minutes (timer)", "study", "easy", 15),
    ("📚 Review notes for 15 minutes", "study", "easy", 12),
    ("📚 Practice 5 problems or questions", "study", "medium", 18),

    ("🏃 Move: 10-minute walk or stretch", "fitness", "easy", 12),
    ("🏃 Move: 15 minutes (your choice)", "fitness", "medium", 18),
    ("🏃 Try a short strength set (5–10 mins)", "fitness", "hard", 25),

    ("🌙 Screen-off 30 minutes before bed", "sleep", "medium", 18),
    ("🌙 Plan bedtime + wake time (write it)", "sleep", "easy", 12),

    ("🥗 Add one fruit/veg today", "nutrition", "easy", 12),
    ("🥗 Drink an extra glass of water", "nutrition", "easy", 10),
    ("🥗 Build a balanced plate (photo optional)", "nutrition", "medium", 18),

    ("🧠 3 lines: what went well today?", "reflection", "easy", 12),
    ("🧠 Name 1 worry + 1 tiny next step", "reflection", "medium", 18),

    ("🤝 Send a kind message to someone", "social", "easy", 12),
    ("🤝 Help at home for 10 minutes", "social", "medium", 18),
]

MISSION_TO_STAT = {
    "study": "knowledge",
    "fitness": "guts",
    "sleep": "proficiency",
    "nutrition": "kindness",
    "reflection": "charm",
    "social": "kindness",
}

def _pick_daily_set(seed_key: str, count: int = 5):
    rng = random.Random(seed_key)
    pool = MISSION_CATALOG[:]
    rng.shuffle(pool)

    chosen = []
    needed_types = ["study", "fitness", "sleep", "nutrition", "reflection"]
    for t in needed_types:
        for item in pool:
            if item[1] == t and item not in chosen:
                chosen.append(item)
                break

    for item in pool:
        if len(chosen) >= count:
            break
        if item not in chosen:
            chosen.append(item)

    return chosen[:count]

def ensure_daily_missions_exist(db: Session, for_date):
    existing = db.query(Mission).filter(
        Mission.created_for_date == for_date,
        Mission.created_by_system == True,
        Mission.is_hidden == False,
    ).count()

    if existing >= 5:
        return

    seed_key = f"{for_date.isoformat()}-soulsync"
    daily = _pick_daily_set(seed_key, count=5)

    for title, mtype, diff, xp in daily:
        db.add(Mission(
            title=title,
            type=mtype,
            difficulty=diff,
            xp_reward=xp,
            is_hidden=False,
            geo_rule_json=None,
            created_for_date=for_date,
            created_by_system=True
        ))
    db.flush()

def ensure_assignments_for_user(db: Session, user_id: int, tz_name: str):
    day = today_in_tz(tz_name)
    ensure_daily_missions_exist(db, day)

    missions = db.query(Mission).filter(
        Mission.created_for_date == day,
        Mission.created_by_system == True,
        Mission.is_hidden == False,
    ).all()

    existing = {
        (a.mission_id, a.date)
        for a in db.query(MissionAssignment).filter(
            MissionAssignment.user_id == user_id,
            MissionAssignment.date == day
        ).all()
    }

    for m in missions:
        if (m.id, day) not in existing:
            db.add(MissionAssignment(
                user_id=user_id,
                mission_id=m.id,
                date=day,
                status="pending",
                proof_json=None,
                completed_at=None
            ))
    db.flush()
    return day

def _streak_bonus_multiplier(streak_count: int) -> float:
    if streak_count <= 0:
        return 0.0
    return min(0.30, 0.05 * streak_count)

def _update_streak_for_day(db: Session, user_id: int, day):
    prof = db.query(Profile).filter(Profile.user_id == user_id).one()
    todays = db.query(MissionAssignment).filter(
        MissionAssignment.user_id == user_id,
        MissionAssignment.date == day
    ).all()

    if not todays:
        return
    if not all(x.status == "completed" for x in todays):
        return

    yesterday = day - timedelta(days=1)
    y_assign = db.query(MissionAssignment).filter(
        MissionAssignment.user_id == user_id,
        MissionAssignment.date == yesterday
    ).all()

    y_done = bool(y_assign) and all(x.status == "completed" for x in y_assign)

    if y_done:
        prof.streak_count += 1
    else:
        prof.streak_count = max(1, prof.streak_count)

    db.add(AuditLog(
        user_id=user_id,
        event_type="streak_updated",
        meta_json=json.dumps({"date": day.isoformat(), "streak": prof.streak_count})
    ))
    db.flush()

def complete_assignment(db: Session, assignment_id: int, user_id: int, proof: dict | None = None) -> dict:
    a = db.query(MissionAssignment).filter(
        MissionAssignment.id == assignment_id,
        MissionAssignment.user_id == user_id
    ).one()

    if a.status == "completed":
        return {"ok": True, "message": "Already completed."}

    m = db.query(Mission).filter(Mission.id == a.mission_id).one()
    prof = db.query(Profile).filter(Profile.user_id == user_id).one()

    bonus_mult = _streak_bonus_multiplier(prof.streak_count)
    bonus = int(round(m.xp_reward * bonus_mult))
    total_xp = m.xp_reward + bonus

    stat_type = MISSION_TO_STAT.get(m.type, "knowledge")
    grant_stat_xp(db, user_id, stat_type, total_xp)

    a.status = "completed"
    a.completed_at = datetime.utcnow()
    a.proof_json = json.dumps(proof or {})

    db.add(AuditLog(
        user_id=user_id,
        event_type="mission_completed",
        meta_json=json.dumps({
            "assignment_id": assignment_id,
            "mission_id": m.id,
            "xp_base": m.xp_reward,
            "xp_bonus": bonus,
            "xp_total": total_xp,
            "stat_type": stat_type
        })
    ))
    db.flush()

    _update_streak_for_day(db, user_id, a.date)

    return {"ok": True, "message": f"+{total_xp} XP to {stat_type} (base {m.xp_reward} + bonus {bonus})"}

def get_todays_assignments(db: Session, user_id: int, tz_name: str):
    day = ensure_assignments_for_user(db, user_id, tz_name)
    rows = (
        db.query(MissionAssignment, Mission)
        .join(Mission, Mission.id == MissionAssignment.mission_id)
        .filter(MissionAssignment.user_id == user_id, MissionAssignment.date == day)
        .order_by(Mission.difficulty.asc())
        .all()
    )
    return day, rows

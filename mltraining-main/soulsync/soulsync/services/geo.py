from __future__ import annotations

import json
import math
from datetime import datetime
from sqlalchemy.orm import Session

from soulsync.constants import HIDDEN_SPOTS
from soulsync.models import Mission, MissionAssignment, AuditLog
from soulsync.services.timeutil import today_in_tz


def haversine_m(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    """Great-circle distance between two points in meters."""
    R = 6371000.0
    phi1, phi2 = math.radians(lat1), math.radians(lat2)
    dphi = math.radians(lat2 - lat1)
    dlambda = math.radians(lon2 - lon1)

    a = math.sin(dphi / 2) ** 2 + math.cos(phi1) * math.cos(phi2) * math.sin(dlambda / 2) ** 2
    return 2 * R * math.atan2(math.sqrt(a), math.sqrt(1 - a))


def ensure_hidden_missions_for_day(db: Session, day):
    """Create hidden mission definitions for a day if missing."""
    existing = db.query(Mission).filter(
        Mission.created_for_date == day,
        Mission.is_hidden == True,
        Mission.created_by_system == True
    ).count()

    if existing >= len(HIDDEN_SPOTS):
        return

    for spot in HIDDEN_SPOTS:
        geo_rule_json = json.dumps(spot["rule"])
        dupe = db.query(Mission).filter(
            Mission.created_for_date == day,
            Mission.is_hidden == True,
            Mission.title == spot["title"]
        ).one_or_none()
        if dupe:
            continue

        db.add(Mission(
            title=spot["title"],
            type=spot["type"],
            difficulty=spot["difficulty"],
            xp_reward=spot["xp_reward"],
            is_hidden=True,
            geo_rule_json=geo_rule_json,
            created_for_date=day,
            created_by_system=True
        ))
    db.flush()


def _within_radius(rule: dict, lat: float, lon: float) -> bool:
    if rule.get("kind") != "radius":
        return False
    d = haversine_m(lat, lon, float(rule["lat"]), float(rule["lon"]))
    return d <= float(rule["radius_m"])


def find_nearby_hidden_missions(db: Session, day, lat: float, lon: float):
    missions = db.query(Mission).filter(
        Mission.created_for_date == day,
        Mission.is_hidden == True,
        Mission.created_by_system == True
    ).all()

    nearby = []
    for m in missions:
        if not m.geo_rule_json:
            continue
        try:
            rule = json.loads(m.geo_rule_json)
        except Exception:
            continue

        if _within_radius(rule, lat, lon):
            nearby.append((m, rule))
    return nearby


def unlock_hidden_missions(
    db: Session,
    user_id: int,
    tz_name: str,
    lat: float,
    lon: float,
    max_unlock: int = 3
) -> dict:
    """
    Unlock nearby hidden missions for today.
    Privacy: coordinates are NOT stored; only unlock events are logged.
    """
    day = today_in_tz(tz_name)
    ensure_hidden_missions_for_day(db, day)

    nearby = find_nearby_hidden_missions(db, day, lat, lon)
    if not nearby:
        return {"day": day, "unlocked": [], "message": "No hidden missions nearby right now. Try again later!"}

    unlocked = []
    for m, rule in nearby[:max_unlock]:
        exists = db.query(MissionAssignment).filter(
            MissionAssignment.user_id == user_id,
            MissionAssignment.mission_id == m.id,
            MissionAssignment.date == day
        ).one_or_none()
        if exists:
            continue

        db.add(MissionAssignment(
            user_id=user_id,
            mission_id=m.id,
            date=day,
            status="pending",
            proof_json=None,
            completed_at=None
        ))
        db.flush()

        db.add(AuditLog(
            user_id=user_id,
            event_type="hidden_mission_unlocked",
            meta_json=json.dumps({
                "mission_id": m.id,
                "date": day.isoformat(),
                "rule_kind": rule.get("kind"),
                "radius_m": rule.get("radius_m"),
                "source": "browser_geolocation"
            }),
            created_at=datetime.utcnow()
        ))

        unlocked.append({"mission_id": m.id, "title": m.title})

    db.flush()
    if unlocked:
        return {"day": day, "unlocked": unlocked, "message": f"Unlocked {len(unlocked)} hidden mission(s)! 🎉"}
    return {"day": day, "unlocked": [], "message": "Hidden missions found, but you already unlocked them today ✅"}

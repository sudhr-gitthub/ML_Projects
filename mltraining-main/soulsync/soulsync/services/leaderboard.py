from __future__ import annotations

import json
from dataclasses import dataclass
from datetime import datetime, timedelta, timezone
from typing import Literal

from sqlalchemy.orm import Session

from soulsync.models import User, Profile, AuditLog, RankSnapshot

Scope = Literal["global", "local"]
Period = Literal["weekly", "alltime"]
LocalBy = Literal["city", "region"]

MISSION_EVENT = "mission_completed"

# Gentle anti-cheat defaults (tunable)
MAX_XP_PER_DAY = 600
MAX_MISSIONS_PER_DAY = 18


def _safe_json_loads(s: str | None) -> dict:
    if not s:
        return {}
    try:
        return json.loads(s)
    except Exception:
        return {}


def week_start_utc(dt: datetime | None = None) -> datetime:
    """Monday 00:00 UTC for the week containing dt."""
    dt = dt or datetime.now(timezone.utc)
    if dt.tzinfo is None:
        dt = dt.replace(tzinfo=timezone.utc)
    start = dt - timedelta(days=dt.weekday())
    return datetime(start.year, start.month, start.day, tzinfo=timezone.utc)


def _period_since(period: Period, now_utc: datetime) -> datetime | None:
    return week_start_utc(now_utc) if period == "weekly" else None


def _daily_key(dt: datetime) -> str:
    # stored timestamps are naive UTC in our DB; treat them as UTC
    if dt.tzinfo is not None:
        dt = dt.astimezone(timezone.utc).replace(tzinfo=None)
    return dt.date().isoformat()


def _local_filter(user: User, local_by: LocalBy, local_value: str | None) -> bool:
    if not local_value:
        return False
    val = local_value.strip().lower()
    if local_by == "city":
        return (user.city or "").strip().lower() == val
    return (user.region or "").strip().lower() == val


@dataclass
class LeaderboardRow:
    user_id: int
    handle: str
    avatar_url: str | None
    xp: int
    rank: int
    city: str | None = None
    region: str | None = None


def _is_suspicious(db: Session, user_id: int, since: datetime | None) -> bool:
    q = db.query(AuditLog).filter(
        AuditLog.user_id == user_id,
        AuditLog.event_type == MISSION_EVENT
    )
    if since is not None:
        q = q.filter(AuditLog.created_at >= since.replace(tzinfo=None))

    logs = q.all()
    if not logs:
        return False

    xp_by_day: dict[str, int] = {}
    missions_by_day: dict[str, int] = {}

    for log in logs:
        day = _daily_key(log.created_at)
        meta = _safe_json_loads(log.meta_json)
        xp_total = int(meta.get("xp_total", 0) or 0)

        xp_by_day[day] = xp_by_day.get(day, 0) + xp_total
        missions_by_day[day] = missions_by_day.get(day, 0) + 1

    if any(xp > MAX_XP_PER_DAY for xp in xp_by_day.values()):
        return True
    if any(cnt > MAX_MISSIONS_PER_DAY for cnt in missions_by_day.values()):
        return True
    return False


def compute_user_xp(db: Session, user_id: int, since: datetime | None) -> int:
    q = db.query(AuditLog).filter(
        AuditLog.user_id == user_id,
        AuditLog.event_type == MISSION_EVENT
    )
    if since is not None:
        q = q.filter(AuditLog.created_at >= since.replace(tzinfo=None))

    total = 0
    for log in q.all():
        meta = _safe_json_loads(log.meta_json)
        total += int(meta.get("xp_total", 0) or 0)
    return total


def cleanup_snapshots_for_optout(db: Session) -> None:
    opted_out_ids = [u.id for u in db.query(User).filter(User.consent_leaderboard == False).all()]
    if not opted_out_ids:
        return
    db.query(RankSnapshot).filter(RankSnapshot.user_id.in_(opted_out_ids)).delete(synchronize_session=False)
    db.flush()


def recalc_leaderboard(
    db: Session,
    scope: Scope,
    period: Period,
    local_by: LocalBy = "region",
    local_value: str | None = None,
    limit: int = 50,
    now_utc: datetime | None = None
) -> list[LeaderboardRow]:
    """Recalculate RankSnapshot and return top rows.

    Rules:
    - Only includes opted-in users.
    - Local scope filters by city/region.
    - Weekly uses Monday 00:00 UTC.
    - Suspicious users are gently excluded.
    """
    now_utc = now_utc or datetime.now(timezone.utc)
    since = _period_since(period, now_utc)

    cleanup_snapshots_for_optout(db)

    users = db.query(User).filter(User.consent_leaderboard == True).all()
    if scope == "local":
        users = [u for u in users if _local_filter(u, local_by, local_value)]

    rows: list[LeaderboardRow] = []
    for u in users:
        if _is_suspicious(db, u.id, since):
            continue
        xp = compute_user_xp(db, u.id, since)
        prof = db.query(Profile).filter(Profile.user_id == u.id).one_or_none()
        rows.append(LeaderboardRow(
            user_id=u.id,
            handle=u.handle,
            avatar_url=(prof.avatar_url if prof else None),
            xp=xp,
            rank=0,
            city=u.city,
            region=u.region
        ))

    rows.sort(key=lambda r: (-r.xp, r.handle.lower()))

    for idx, r in enumerate(rows, start=1):
        r.rank = idx

    rows = rows[:limit]

    # Refresh snapshots for this scope/period
    snap_q = db.query(RankSnapshot).filter(RankSnapshot.scope == scope, RankSnapshot.period == period)
    if since is not None:
        snap_q = snap_q.filter(RankSnapshot.created_at >= since.replace(tzinfo=None))
    snap_q.delete(synchronize_session=False)

    for r in rows:
        db.add(RankSnapshot(
            user_id=r.user_id,
            scope=scope,
            period=period,
            xp=r.xp,
            rank=r.rank,
            created_at=now_utc.replace(tzinfo=None)
        ))

    db.flush()
    return rows

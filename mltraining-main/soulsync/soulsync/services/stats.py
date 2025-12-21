from __future__ import annotations
from datetime import datetime
from sqlalchemy.orm import Session
from soulsync.constants import XP_BASE, MAX_LEVEL
from soulsync.models import Stat

def xp_needed_for_level(level: int, base: int = XP_BASE) -> int:
    """XP needed to advance from level -> level+1 using base*n^2."""
    n = max(1, int(level))
    return int(base * (n ** 2))

def apply_xp_and_level(stat: Stat, xp_gain: int, base: int = XP_BASE) -> Stat:
    if xp_gain <= 0:
        return stat
    stat.xp += int(xp_gain)
    while stat.level < MAX_LEVEL:
        need = xp_needed_for_level(stat.level, base=base)
        if stat.xp >= need:
            stat.xp -= need
            stat.level += 1
        else:
            break
    stat.updated_at = datetime.utcnow()
    return stat

def get_or_create_stat(db: Session, user_id: int, stat_type: str) -> Stat:
    st = db.query(Stat).filter(Stat.user_id == user_id, Stat.type == stat_type).one_or_none()
    if st:
        return st
    st = Stat(user_id=user_id, type=stat_type, level=1, xp=0)
    db.add(st)
    db.flush()
    return st

def grant_stat_xp(db: Session, user_id: int, stat_type: str, xp_gain: int) -> Stat:
    st = get_or_create_stat(db, user_id, stat_type)
    st = apply_xp_and_level(st, xp_gain)
    db.add(st)
    return st

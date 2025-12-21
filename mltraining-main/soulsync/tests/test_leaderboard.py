import json
from datetime import datetime, timezone, timedelta

from soulsync.models import User, Profile, AuditLog
from soulsync.services.leaderboard import recalc_leaderboard


def add_user(db, email, handle, optin=True, city=None, region=None):
    u = User(email=email, handle=handle, consent_leaderboard=optin, consent_location=False, city=city, region=region)
    db.add(u)
    db.flush()
    db.add(Profile(user_id=u.id, timezone="UTC", streak_count=0, goals_json='{"goals":["Study smarter"],"note":""}'))
    db.flush()
    return u


def add_xp_log(db, user_id, xp_total, when_utc):
    db.add(AuditLog(
        user_id=user_id,
        event_type="mission_completed",
        meta_json=json.dumps({"xp_total": xp_total}),
        created_at=when_utc.replace(tzinfo=None)
    ))


def test_leaderboard_optin_and_ranking(db_session):
    now = datetime.now(timezone.utc)

    u1 = add_user(db_session, "a@x.com", "Alpha_01", optin=True, region="TN")
    u2 = add_user(db_session, "b@x.com", "Beta_02", optin=True, region="TN")
    u3 = add_user(db_session, "c@x.com", "Gamma_03", optin=False, region="TN")

    add_xp_log(db_session, u1.id, 50, now - timedelta(days=1))
    add_xp_log(db_session, u2.id, 120, now - timedelta(days=1))
    add_xp_log(db_session, u3.id, 999, now - timedelta(days=1))
    db_session.commit()

    rows = recalc_leaderboard(db_session, scope="global", period="alltime", limit=10, now_utc=now)
    db_session.commit()

    handles = [r.handle for r in rows]
    assert "Gamma_03" not in handles
    assert handles[0] == "Beta_02"
    assert handles[1] == "Alpha_01"


def test_optout_disappears_after_refresh(db_session):
    now = datetime.now(timezone.utc)

    u1 = add_user(db_session, "a@x.com", "Alpha_01", optin=True, region="TN")
    add_xp_log(db_session, u1.id, 100, now - timedelta(hours=2))
    db_session.commit()

    rows = recalc_leaderboard(db_session, scope="global", period="weekly", limit=10, now_utc=now)
    db_session.commit()
    assert any(r.handle == "Alpha_01" for r in rows)

    u1.consent_leaderboard = False
    db_session.commit()

    rows2 = recalc_leaderboard(db_session, scope="global", period="weekly", limit=10, now_utc=now)
    db_session.commit()
    assert all(r.handle != "Alpha_01" for r in rows2)

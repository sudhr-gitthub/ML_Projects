from datetime import date
import json

from soulsync.models import Mission, MissionAssignment, AuditLog, Profile
from soulsync.services.geo import haversine_m, unlock_hidden_missions


def test_haversine_reasonable():
    assert haversine_m(10.0, 10.0, 10.0, 10.0) < 0.01


def test_unlock_creates_assignment_and_audit(db_session, test_user):
    prof = db_session.query(Profile).filter_by(user_id=test_user.id).one()
    prof.timezone = "UTC"
    db_session.commit()

    day = date.today()
    rule = {"kind": "radius", "lat": 10.0, "lon": 10.0, "radius_m": 500}

    m = Mission(
        title="🗺️ Hidden Test Quest",
        type="study",
        difficulty="easy",
        xp_reward=20,
        is_hidden=True,
        geo_rule_json=json.dumps(rule),
        created_for_date=day,
        created_by_system=True
    )
    db_session.add(m)
    db_session.commit()

    res = unlock_hidden_missions(
        db=db_session,
        user_id=test_user.id,
        tz_name="UTC",
        lat=10.0005,
        lon=10.0005
    )
    db_session.commit()

    assert len(res["unlocked"]) >= 1

    a = db_session.query(MissionAssignment).filter_by(user_id=test_user.id, mission_id=m.id, date=day).one_or_none()
    assert a is not None
    assert a.status == "pending"

    logs = db_session.query(AuditLog).filter_by(user_id=test_user.id, event_type="hidden_mission_unlocked").all()
    assert len(logs) >= 1
    meta = logs[-1].meta_json or ""
    assert "latitude" not in meta and "longitude" not in meta and "lat" not in meta and "lon" not in meta

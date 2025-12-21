from datetime import date
from soulsync.models import Mission, MissionAssignment, Stat, Profile
from soulsync.services.missions import complete_assignment
from soulsync.services.users import ensure_all_stats

def setup_day(db, user_id: int, day: date):
    m1 = Mission(title="Study", type="study", difficulty="easy", xp_reward=10, is_hidden=False,
                geo_rule_json=None, created_for_date=day, created_by_system=True)
    m2 = Mission(title="Sleep", type="sleep", difficulty="easy", xp_reward=10, is_hidden=False,
                geo_rule_json=None, created_for_date=day, created_by_system=True)
    db.add_all([m1, m2])
    db.flush()

    a1 = MissionAssignment(user_id=user_id, mission_id=m1.id, date=day, status="pending")
    a2 = MissionAssignment(user_id=user_id, mission_id=m2.id, date=day, status="pending")
    db.add_all([a1, a2])
    db.flush()
    return a1, a2

def test_complete_assignment_grants_xp_and_updates_status(db_session, test_user):
    ensure_all_stats(db_session, test_user.id)
    db_session.commit()

    day = date(2025, 1, 1)
    a1, a2 = setup_day(db_session, test_user.id, day)
    db_session.commit()

    res = complete_assignment(db_session, a1.id, test_user.id, proof={"kind": "note", "value": "done"})
    db_session.commit()
    assert res["ok"] is True

    a1_db = db_session.query(MissionAssignment).filter_by(id=a1.id).one()
    assert a1_db.status == "completed"

    stat = db_session.query(Stat).filter_by(user_id=test_user.id, type="knowledge").one()
    assert stat.xp >= 10

def test_streak_increments_only_when_all_done(db_session, test_user):
    ensure_all_stats(db_session, test_user.id)
    prof = db_session.query(Profile).filter_by(user_id=test_user.id).one()
    prof.streak_count = 0
    db_session.commit()

    day = date(2025, 1, 2)
    a1, a2 = setup_day(db_session, test_user.id, day)
    db_session.commit()

    complete_assignment(db_session, a1.id, test_user.id, proof=None)
    db_session.commit()

    prof = db_session.query(Profile).filter_by(user_id=test_user.id).one()
    assert prof.streak_count == 0

    complete_assignment(db_session, a2.id, test_user.id, proof=None)
    db_session.commit()

    prof = db_session.query(Profile).filter_by(user_id=test_user.id).one()
    assert prof.streak_count == 1

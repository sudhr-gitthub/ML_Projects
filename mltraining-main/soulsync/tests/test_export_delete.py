from datetime import date
import json

from soulsync.models import (
    User, Profile, Stat,
    Mission, MissionAssignment,
    JournalEntry, VoiceMemory, VoiceMessage
)
from soulsync.services.export import export_user_data_minimal
from soulsync.services.account import delete_account


def test_export_contains_required_sections_and_is_minimal(db_session):
    u = User(email="exp@x.com", handle="Exporter_01", consent_leaderboard=False, consent_location=False)
    db_session.add(u)
    db_session.flush()

    db_session.add(Profile(user_id=u.id, timezone="UTC", streak_count=2, goals_json='{"goals":["Study smarter"],"note":""}'))
    db_session.add(Stat(user_id=u.id, type="knowledge", level=2, xp=5))
    db_session.flush()

    m = Mission(title="Test Mission", type="study", difficulty="easy", xp_reward=10, is_hidden=False,
                geo_rule_json=None, created_for_date=date.today(), created_by_system=True)
    db_session.add(m)
    db_session.flush()

    db_session.add(MissionAssignment(user_id=u.id, mission_id=m.id, date=date.today(), status="pending"))
    db_session.add(JournalEntry(user_id=u.id, mood="okay", text="Hello journal", tags="test"))
    db_session.add(VoiceMemory(user_id=u.id, kind="journal", content="Memory content", vector=None))

    # chat history exists but must NOT be exported
    db_session.add(VoiceMessage(user_id=u.id, role="user", text="Hi", embedding_vector=None))

    db_session.commit()

    data = export_user_data_minimal(db_session, u.id)

    assert "user" in data
    assert "profile" in data
    assert "stats" in data
    assert "missions" in data
    assert "journal" in data
    assert "voice_memory" in data

    assert "voice_messages" not in data
    assert "audit_log" not in data


def test_delete_account_wipes_everything(db_session):
    u = User(email="del@x.com", handle="DeleteMe_01", consent_leaderboard=True, consent_location=True)
    db_session.add(u)
    db_session.flush()

    db_session.add(Profile(user_id=u.id, timezone="UTC", streak_count=0, goals_json='{"goals":["Sleep better"],"note":""}'))
    db_session.add(Stat(user_id=u.id, type="knowledge", level=1, xp=0))
    db_session.commit()

    delete_account(db_session, u.id)
    db_session.commit()

    assert db_session.query(User).filter(User.id == u.id).one_or_none() is None
    assert db_session.query(Profile).filter(Profile.user_id == u.id).one_or_none() is None
    assert db_session.query(Stat).filter(Stat.user_id == u.id).count() == 0

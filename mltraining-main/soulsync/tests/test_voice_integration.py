from soulsync.models import VoiceMessage, Profile
from soulsync.services.voice import chat_once


def test_voice_chat_fallback_saves_messages(db_session, test_user):
    prof = db_session.query(Profile).filter_by(user_id=test_user.id).one_or_none()
    if not prof:
        prof = Profile(user_id=test_user.id, timezone="UTC", streak_count=0, goals_json='{"goals":["Study smarter"],"note":""}')
        db_session.add(prof)
        db_session.commit()

    res = chat_once(db_session, test_user.id, "I feel stuck with homework.")
    db_session.commit()

    assert res["assistant"]

    msgs = db_session.query(VoiceMessage).filter_by(user_id=test_user.id).order_by(VoiceMessage.created_at.asc()).all()
    assert len(msgs) >= 2
    assert msgs[-2].role == "user"
    assert msgs[-1].role == "assistant"


def test_voice_moderation_blocks_toxic(db_session, test_user):
    res = chat_once(db_session, test_user.id, "You are stupid")
    db_session.commit()
    assert res["flagged"] is True

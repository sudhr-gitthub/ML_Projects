import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from soulsync.models import Base, User, Profile

@pytest.fixture()
def db_session():
    engine = create_engine("sqlite:///:memory:", future=True)
    Base.metadata.create_all(bind=engine)
    Session = sessionmaker(bind=engine, autoflush=False, autocommit=False, future=True)
    session = Session()
    yield session
    session.close()

@pytest.fixture()
def test_user(db_session):
    u = User(email="test@example.com", handle="Tester_01", consent_leaderboard=False, consent_location=False)
    db_session.add(u)
    db_session.flush()
    p = Profile(user_id=u.id, timezone="UTC", streak_count=0, goals_json='{"goals":["Study smarter"],"note":""}')
    db_session.add(p)
    db_session.commit()
    return u

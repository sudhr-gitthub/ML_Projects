from datetime import date
import json

from soulsync.db import get_session, init_db
from soulsync.models import Base, Mission

def run():
    init_db(Base)
    db = get_session()
    today = date.today()

    if db.query(Mission).count() > 0:
        print("Missions already seeded.")
        return

    missions = [
        Mission(title="📚 20-minute study sprint", type="study", difficulty="easy", xp_reward=15,
                is_hidden=False, geo_rule_json=None, created_for_date=today, created_by_system=True),
        Mission(title="🏃 10-minute walk or stretch", type="fitness", difficulty="easy", xp_reward=12,
                is_hidden=False, geo_rule_json=None, created_for_date=today, created_by_system=True),
        Mission(title="🌙 Screen-off 30 minutes before bed", type="sleep", difficulty="medium", xp_reward=18,
                is_hidden=False, geo_rule_json=None, created_for_date=today, created_by_system=True),
        Mission(title="🥗 Add one fruit/veg today", type="nutrition", difficulty="easy", xp_reward=12,
                is_hidden=False, geo_rule_json=None, created_for_date=today, created_by_system=True),
        Mission(title="🧠 3 lines: what went well today?", type="reflection", difficulty="easy", xp_reward=12,
                is_hidden=False, geo_rule_json=None, created_for_date=today, created_by_system=True),

        Mission(title="🗺️ Hidden: Visit a library & take a calm breath", type="study", difficulty="medium", xp_reward=25,
                is_hidden=True,
                geo_rule_json=json.dumps({"kind": "radius", "lat": 12.9716, "lon": 77.5946, "radius_m": 250}),
                created_for_date=today, created_by_system=True),
    ]

    db.add_all(missions)
    db.commit()
    print("Seeded missions:", len(missions))

if __name__ == "__main__":
    run()

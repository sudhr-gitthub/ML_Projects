from soulsync.services.stats import xp_needed_for_level, apply_xp_and_level
from soulsync.models import Stat

def test_xp_needed_curve_base_n2():
    assert xp_needed_for_level(1) == 20
    assert xp_needed_for_level(2) == 80
    assert xp_needed_for_level(3) == 180

def test_apply_xp_levels_up():
    s = Stat(user_id=1, type="knowledge", level=1, xp=0)
    apply_xp_and_level(s, 25)
    assert s.level == 2
    assert s.xp == 5

    apply_xp_and_level(s, 90)
    assert s.level == 3
    assert s.xp == 15

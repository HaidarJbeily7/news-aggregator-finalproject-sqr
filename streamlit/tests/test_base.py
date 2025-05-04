from src.base import one_equals_one_here


def test_one_equals_one():
    """Test that one equals one directly and via imported function."""
    assert one_equals_one_here() == 1

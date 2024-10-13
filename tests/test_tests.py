import pytest

def test_fail_once_1() -> None:
    test_fail_once_1.__dict__["n"] = test_fail_once_1.__dict__.get("n", 0) + 1
    if test_fail_once_1.__dict__["n"] == 1:
        pytest.fail("oops")


def test_fail_twice_23() -> None:
    test_fail_twice_23.__dict__["n"] = test_fail_twice_23.__dict__.get("n", 0) + 1
    if test_fail_twice_23.__dict__["n"] in [2, 3]:
        pytest.fail("oops")


def test_foo1() -> None:
    pass


def test_foo2() -> None:
    pass

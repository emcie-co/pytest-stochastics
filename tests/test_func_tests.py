import pytest


@pytest.fixture
def foofix() -> bool:
    return True


def test_fail() -> None:
    assert False


def test_pass() -> None:
    pass


def test_fixture_true(foofix: bool) -> None:
    assert foofix


def test_pass_once_1() -> None:
    test_pass_once_1.__dict__["n"] = test_pass_once_1.__dict__.get("n", 0) + 1
    assert test_pass_once_1.__dict__["n"] in [1]


def test_fail_once_1() -> None:
    test_fail_once_1.__dict__["n"] = test_fail_once_1.__dict__.get("n", 0) + 1
    assert test_fail_once_1.__dict__["n"] not in [1]


def test_pass_twice_23() -> None:
    test_pass_twice_23.__dict__["n"] = test_pass_twice_23.__dict__.get("n", 0) + 1
    assert test_pass_twice_23.__dict__["n"] in [2, 3]


def test_fail_twice_23() -> None:
    test_fail_twice_23.__dict__["n"] = test_fail_twice_23.__dict__.get("n", 0) + 1
    assert test_fail_twice_23.__dict__["n"] not in [2, 3]

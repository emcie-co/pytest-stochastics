import pytest

"""This file contains tests for the Stochastics wrapper to wrap."""


@pytest.fixture
def foofix() -> bool:
    """Fixture that returns True."""
    return True


def test_fail() -> None:
    """Test that always fails."""
    assert False


@pytest.mark.parametrize("true", (True, True))
def test_pass(true: bool) -> None:
    """Test that always passes."""
    assert true


@pytest.mark.parametrize("foo", (1, 2))
def test_marked_pass_once_2(foo: int) -> None:
    """Test that passes only the 2nd time it's run (fails all consecutive)."""

    assert foo == 2


def test_fixture_true(foofix: bool) -> None:
    """Test that passes if the fixture returns True."""
    assert foofix


def test_pass_once_1() -> None:
    """Test that passes only the 1st time it's run (fails all consecutive)."""

    test_pass_once_1.__dict__["n"] = test_pass_once_1.__dict__.get("n", 0) + 1
    assert test_pass_once_1.__dict__["n"] in [1]


def test_fail_once_1() -> None:
    """Test that fails only the 1st time it's run (passess all consecutive)."""

    test_fail_once_1.__dict__["n"] = test_fail_once_1.__dict__.get("n", 0) + 1
    assert test_fail_once_1.__dict__["n"] not in [1]


def test_pass_twice_23() -> None:
    """Test that passes only the 2nd and 3rd time it's run (fails all other)."""

    test_pass_twice_23.__dict__["n"] = test_pass_twice_23.__dict__.get("n", 0) + 1
    assert test_pass_twice_23.__dict__["n"] in [2, 3]


def test_fail_twice_23() -> None:
    """Test that fails only the 2nd and 3rd time it's run (passes all other)."""

    test_fail_twice_23.__dict__["n"] = test_fail_twice_23.__dict__.get("n", 0) + 1
    assert test_fail_twice_23.__dict__["n"] not in [2, 3]

from typing import Any, NoReturn
import pytest
from unittest.mock import patch
from pathlib import Path
from pytest_stochastics.logger import Logger

from pytest_stochastics.helpers import read_git_branch


@pytest.fixture
def mock_logger() -> Logger:
    return Logger(prefix="MOCK= ")


@pytest.fixture
def mock_git_directory(tmp_path: Path) -> tuple[Path, Path]:
    git_dir = tmp_path / ".git"
    git_dir.mkdir()
    head_file = git_dir / "HEAD"
    return tmp_path, head_file


def test_read_git_branch_success(mock_logger: Logger, mock_git_directory: tuple[Path, Path]) -> None:
    tmp_path, head_file = mock_git_directory
    head_content = "ref: refs/heads/main\n"
    head_file.write_text(head_content)

    with patch("os.path.abspath", return_value=str(tmp_path)):
        branch = read_git_branch(mock_logger)

    assert branch == "main"


def test_read_git_branch_no_git_directory(mock_logger: Logger, tmp_path: Path) -> None:
    with patch("os.path.abspath", return_value=str(tmp_path)):
        with patch("os.path.dirname", side_effect=[str(tmp_path), "/"]):
            branch = read_git_branch(mock_logger)

    assert branch == ""


def test_read_git_branch_permission_error(mock_logger: Logger, mock_git_directory: tuple[Path, Path]) -> None:
    tmp_path, _ = mock_git_directory

    def raise_permission_error(*args: list[Any], **kwargs: dict[Any, Any]) -> NoReturn:
        raise PermissionError("Permission denied")

    with patch("os.path.abspath", return_value=str(tmp_path)):
        with patch("os.listdir", side_effect=raise_permission_error):
            branch = read_git_branch(mock_logger)

    assert branch == ""


def test_read_git_branch_io_error(mock_logger: Logger, mock_git_directory: tuple[Path, Path]) -> None:
    tmp_path, _ = mock_git_directory

    def raise_io_error(*args: list[Any], **kwargs: dict[Any, Any]) -> NoReturn:
        raise IOError("IO Error")

    with patch("os.path.abspath", return_value=str(tmp_path)):
        with patch("pathlib.Path.open", side_effect=raise_io_error):
            branch = read_git_branch(mock_logger)

    assert branch == ""


def test_read_git_branch_invalid_content(mock_logger: Logger, mock_git_directory: tuple[Path, Path]) -> None:
    tmp_path, head_file = mock_git_directory
    head_content = "invalid content"
    head_file.write_text(head_content)

    with patch("os.path.abspath", return_value=str(tmp_path)):
        branch = read_git_branch(mock_logger)

    assert branch == ""


def test_read_git_branch_empty_content(mock_logger: Logger, mock_git_directory: tuple[Path, Path]) -> None:
    tmp_path, head_file = mock_git_directory
    head_file.write_text("")

    with patch("os.path.abspath", return_value=str(tmp_path)):
        branch = read_git_branch(mock_logger)

    assert branch == ""

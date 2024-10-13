import os
import re
import sys
from pathlib import Path
from typing import Any, Literal, TextIO


class Logger:
    COLORS = {
        "DEBUG": "\033[94m",  # Blue
        "INFO": "\033[92m",  # Green
        "WARN": "\033[93m",  # Yellow
        "ERROR": "\033[91m",  # Red
    }
    RESET = "\033[0m"

    def __init__(self, file: TextIO = sys.stderr):
        self.file = file

    def _log(self, level: str, *values: Any, sep: str = " ", end: str = "\n") -> None:
        color = self.COLORS.get(level, "")
        prefix = f"{level:<5}"  # This will pad the level to 5 characters
        try:
            message = sep.join(str(value) for value in values)
            colored_message = f"{color}{prefix}: {message}{self.RESET}"
            print(colored_message, end=end, file=self.file)
        except Exception:
            # If coloring fails, fall back to non-colored output
            print(f"{prefix}: {sep.join(str(value) for value in values)}", end=end, file=self.file)

    def debug(self, *values: Any, sep: str = " ", end: str = "\n") -> None:
        self._log("DEBUG", *values, sep=sep, end=end)

    def info(self, *values: Any, sep: str = " ", end: str = "\n") -> None:
        self._log("INFO", *values, sep=sep, end=end)

    def warn(self, *values: Any, sep: str = " ", end: str = "\n") -> None:
        self._log("WARN", *values, sep=sep, end=end)

    def error(self, *values: Any, sep: str = " ", end: str = "\n") -> None:
        self._log("ERROR", *values, sep=sep, end=end)


def _find_git_root(start_path: str = ".") -> Path | None:
    """
    Recursively search for the .git directory up the parent chain.

    :param start_path: The starting path for the search (default is current directory)
    :return: The path containing the .git directory, or None if not found
    """
    current_path = os.path.abspath(start_path)

    while True:
        if ".git" in os.listdir(current_path):
            return Path(current_path)

        parent_path = os.path.dirname(current_path)
        if parent_path == current_path:  # We've reached the root directory
            return None

        current_path = parent_path


def read_git_branch(logger: Logger) -> Any | Literal[""]:
    REGEX_PATTERN_BRANCH = r"^ref: refs/heads/([\w\d_\-+./]+)\s*$"

    branch_name = ""
    try:
        git_path = _find_git_root()
        if git_path is None:
            raise Exception("failed to find `.git`")
        else:
            git_path = git_path / ".git" / "HEAD"
        with git_path.open("r") as f:
            logger.debug(f"File `{git_path}` opened.")
            res = re.search(REGEX_PATTERN_BRANCH, f.read())
            logger.debug(f"Pattern `{REGEX_PATTERN_BRANCH}` matched to: {res}.")
            if res is not None:
                branch_name = res.group(1)
        logger.info(f"Detected branch: {branch_name}")
    except Exception as ex:
        logger.warn(f"Branch discovery failure: {ex}")
        logger.info("No branch detected, will be using fallback")
    return branch_name

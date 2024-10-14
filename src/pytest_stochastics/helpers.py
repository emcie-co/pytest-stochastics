import os
import re
from pytest_stochastics.logger import Logger
from pathlib import Path


def read_git_branch(logger: Logger) -> str:
    REGEX_PATTERN_BRANCH = r"^ref: refs/heads/([\w\d_\-+./]+)\s*$"

    branch_name = ""
    try:
        current_path = os.path.abspath(".")
        git_root = None
        while True:
            try:
                if ".git" in os.listdir(current_path):
                    git_root = Path(current_path)
                    break
            except PermissionError:
                logger.warning(f"Permission denied when accessing {current_path}")
            except OSError as e:
                logger.warning(f"OS error when accessing {current_path}: {e}")

            parent_path = os.path.dirname(current_path)
            if parent_path == current_path:
                break
            current_path = parent_path

        if git_root is None:
            raise Exception("Failed to find `.git` directory")

        git_path = git_root / ".git" / "HEAD"

        try:
            with git_path.open("r") as f:
                logger.debug(f"File `{git_path}` opened.")
                content = f.read()
                res = re.search(REGEX_PATTERN_BRANCH, content)
                logger.debug(f"Pattern `{REGEX_PATTERN_BRANCH}` matched to: {res}.")
                if res is not None:
                    branch_name = res.group(1)
                else:
                    logger.warning(f"Branch pattern not found in file content: {content}")
        except IOError as e:
            logger.error(f"Error reading git HEAD file: {e}")
            raise

        logger.info(f"Detected branch: {branch_name}")
    except Exception as ex:
        logger.warning(f"Branch discovery failure: {ex}")
        logger.info("No branch detected, will be using fallback")
    return branch_name

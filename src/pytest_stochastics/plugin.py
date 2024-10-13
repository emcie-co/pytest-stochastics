from dataclasses import dataclass, field
import sys
from typing import Any
import pytest
from pathlib import Path
import re
import yaml
import os

print("-- `src/pytest_stochastics/plugin.py` --")

# regex pattern for capturing the checked-out branch name
REGEX_PATTERN_BRANCH = r"^ref: refs/heads/([\w\d_\-+./]+)\s*$"

def find_git_root(start_path:str=".")-> Path | None:
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



def _log(*values: object, sep: str | None = " ", end: str | None = "\n") -> None:
    # ANSI escape codes for colors
    YELLOW_TEXT = "\033[38;2;255;255;0m"  # Bright yellow text
    DARK_BLUE_BG = "\033[48;2;0;0;100m"   # Dark blue background
    RESET = "\033[0m"  # Reset to default
    
    colored_values = [f"{YELLOW_TEXT}{DARK_BLUE_BG}{value}{RESET}" for value in values]
    print(*colored_values, sep=sep, end=end, file=sys.stderr)

# Plugin entry point
def pytest_configure(config: pytest.Config) -> None:
    _log("configuring runner selector...")
    _log(f"== config.rootpath={config.rootpath}")
    _log(f"== config.inipath={config.inipath}")
    _log(f"== config.invocation_params={config.invocation_params}")

    _log("acquiring current branch name")
    branch_name = ""
    try:
        git_path = find_git_root()
        if git_path is None:
            raise Exception("failed to find `.git`")
        else:
            git_path= git_path / ".git" / "HEAD"
        with git_path.open("r") as f:
            _log(f"== file `{git_path}` opened.")
            res = re.search(REGEX_PATTERN_BRANCH, f.read())
            _log(f"== pattern `{REGEX_PATTERN_BRANCH}` matched to: {res}.")
            if res is not None:
                branch_name = res.group(1)
        _log(f"detected branch: {branch_name}")
    except Exception as ex:
        _log(f"?! branch discovery failure: {ex}")
        _log("no branch detected, will be using fallback")

    try:
        with open("pytest_config.yaml") as config_file:
            _log("reading config file")
            raw_yaml = config_file.read()
            _log("parsing yaml")
            parsed_yaml = yaml.safe_load(raw_yaml)
            _log("processing config")
            runner_config = ConfigRunnerStochastics(**parsed_yaml)
            _log("configuring runner")
            _log(f"== config={runner_config}")
            runner_selector = RunnerStochastics(runner_config, config, branch_name)
            _log("registering runner")
            config.pluginmanager.register(runner_selector, "Runner-Selector")
            _log("registered runner")
    except Exception as ex:
        _log(f"ERROR: failed to configure runner: {ex}")


@dataclass
class ConfigRunnerStochastics:
    """Object to hold the parsed configuration yaml."""

    tests: dict[str, dict[str, list[str]]]  # B : S : [T]
    strategies: dict[str, dict[str, int]]
    prototypes: dict[str, str] = field(default_factory=dict)  # B: B

    def __init__(self, **kwarg_entries: dict[str, Any]) -> None:
        self.__dict__.update(kwarg_entries)

    def gen_test_lookup(self, branch: str) -> dict[str, tuple[str, str]]:
        """Transpose the strategies dict and layer them so that every test has its strategy."""

        branch_cursor = branch
        lookup: dict[str, tuple[str, str]] = {}
        while branch_cursor.lower() not in ("", "default"):
            branch_config = self.tests.get(branch_cursor, {})
            if branch_config:
                for strat, tests in branch_config.items():
                    for test in tests:
                        test_id = re.sub(r":{1,}test_", "::test_", test)
                        if test_id not in lookup:
                            lookup[test_id] = (strat, branch_cursor)

            branch_cursor = self.prototypes.get(branch_cursor, "default")
        return lookup


class RunnerStochastics:
    runner_config: ConfigRunnerStochastics
    pytest_config: pytest.Config
    root_path: Path
    branch: str
    lookup_test_strategy: dict[str, tuple[str, str]]  # T : (S, B)

    def __init__(
        self,
        runner_config: ConfigRunnerStochastics,
        pytest_config: pytest.Config,
        current_branch: str,
    ) -> None:
        self.runner_config = runner_config
        self.pytest_config = pytest_config
        self.branch = current_branch

        self.lookup_test_strategy = self.runner_config.gen_test_lookup(self.branch)

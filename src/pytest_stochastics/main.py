from typing import Any

import pytest
from _pytest.config import Notset

from pytest_stochastics.helpers import read_git_branch
from pytest_stochastics.logger import Logger
from pytest_stochastics.runner import RunnerStochastics
from pytest_stochastics.runner_data import RunnerStochasticsConfig, BranchId

PYTEST_STOCHASTICS_CONFIG_PATH = "pytest_stochastics_config.json"


def pytest_addoption(parser: pytest.Parser) -> None:
    group = parser.getgroup("stochastics")
    group.addoption(
        "--branch",
        action="store",
        dest="branch",
        default=None,
        help="Specify the branch name to use for stochastic testing",
    )


def pytest_configure(config: pytest.Config) -> None:
    """Main entry point into the pytest plugin flow."""

    DESIRED_RUNNER_NAME = "pytest_stochastics_runner"

    logger = Logger()
    logger.info("Configuring runner selector...")
    logger.debug(f"config.rootpath={config.rootpath}")
    logger.debug(f"config.inipath={config.inipath}")
    logger.debug(f"config.invocation_params={config.invocation_params}")

    branch_name: str | Notset = config.getoption("branch")
    if not branch_name or isinstance(branch_name, Notset):
        branch_name = read_git_branch(logger)
    logger.info(f"Using branch: {branch_name}")

    try:
        with open(PYTEST_STOCHASTICS_CONFIG_PATH) as config_file:
            logger.info("Config file open, reading config file...")
            raw_json = config_file.read()
            logger.info("Read config file, processing config...")
            runner_config: Any = RunnerStochasticsConfig.from_json(raw_json)  # type: ignore #TODO?
            if not isinstance(runner_config, RunnerStochasticsConfig):
                raise Exception(f"expected `RunnerStochasticsConfig` got {runner_config}")
            logger.info("Config created, configuring runner...")
            logger.debug(f"config={runner_config}")
            runner_selector = RunnerStochastics(BranchId(branch_name), runner_config, logger)
            logger.info("Runner constructed, registering runner with pytest...")
            confirmed_name = config.pluginmanager.register(runner_selector, DESIRED_RUNNER_NAME)
            if confirmed_name is None:
                raise Exception(f"Failed to register `{DESIRED_RUNNER_NAME}` plugin!")
            logger.info(f"Registration of `{confirmed_name}` complete!")
    except Exception as ex:
        logger.error(f"Failed to configure runner: {ex}")

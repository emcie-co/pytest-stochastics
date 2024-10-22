import logging
from logging import Logger

import pytest
from _pytest.config import Notset

from pytest_stochastics.runner import RunnerStochastics
from pytest_stochastics.runner_data import PlanId, RunnerStochasticsConfig

PYTEST_STOCHASTICS_CONFIG_PATH = "pytest_stochastics_config.json"


def pytest_addoption(parser: pytest.Parser) -> None:
    group = parser.getgroup("stochastics")
    group.addoption(
        "--plan",
        action="store",
        dest="plan",
        default=None,
        help="Specify the plan name to use for stochastic testing",
    )
    group.addoption(
        "--plan-config-file",
        action="store",
        dest="plan_config_file",
        default=PYTEST_STOCHASTICS_CONFIG_PATH,
        help="Specify a path to the pytest stochastics config file",
    )


def pytest_configure(config: pytest.Config) -> None:
    """Main entry point into the pytest plugin flow."""

    DESIRED_RUNNER_NAME = "pytest_stochastics_runner"

    requested_log_level = config.getoption("log_cli_level")
    if not requested_log_level or isinstance(requested_log_level, Notset):
        requested_log_level = "ERROR"
    logger = Logger(name=DESIRED_RUNNER_NAME, level=requested_log_level)
    logger.addHandler(logging.StreamHandler())

    plan_name: str | Notset = config.getoption("plan")
    if not plan_name or isinstance(plan_name, Notset):
        plan_name = "default"
    logger.info(f"Selected Stochastics Plan: {plan_name}")

    config_file_path: str | Notset = config.getoption("plan_config_file")
    if not config_file_path or isinstance(config_file_path, Notset):
        config_file_path = PYTEST_STOCHASTICS_CONFIG_PATH
    try:
        runner_config = _load_config(config_file_path)
        logger.debug(f"Loaded runner_config: {runner_config}")
    except Exception as ex:
        logger.error(f"Failed to load runner configuration: {ex}")
        config.add_cleanup(
            lambda: print(
                f"\n{"\033[91m"}Stochastic Runner not used, see error log above (look before test session starts) for details.{"\033[0m"}"
            )
        )
        return

    try:
        runner_selector = RunnerStochastics(PlanId(plan_name), runner_config, logger)
        confirmed_name = config.pluginmanager.register(runner_selector, DESIRED_RUNNER_NAME)
        if confirmed_name is None or confirmed_name != DESIRED_RUNNER_NAME:
            raise Exception(f"Failed to register `{DESIRED_RUNNER_NAME}` plugin!")
        logger.debug(f"Confirmed runner name: {confirmed_name}")
    except Exception as ex:
        logger.error(f"Failed to register runner: {ex}")
        config.add_cleanup(
            lambda: print(
                f"\n{"\033[91m"}Stochastic Runner not registered, see error log above (look before test session starts) for details.{"\033[0m"}"
            )
        )


def _load_config(stochastics_config_path: str) -> RunnerStochasticsConfig:
    with open(stochastics_config_path) as config_file:
        raw_json = config_file.read()
        return RunnerStochasticsConfig.from_json(raw_json)  # type: ignore #TODO?

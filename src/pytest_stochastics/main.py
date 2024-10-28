import logging
from logging import Logger
import rich

import pytest

from pytest_stochastics.runner import RunnerStochastics
from pytest_stochastics.runner_data import PlanId, RunnerStochasticsConfig

PYTEST_STOCHASTICS_CONFIG_PATH = "pytest_stochastics.json"
DESIRED_RUNNER_NAME = "pytest_stochastics_runner"


def pytest_addoption(parser: pytest.Parser) -> None:
    group = parser.getgroup("stochastics")
    group.addoption(
        "--plan",
        action="store",
        dest="plan",
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

    requested_log_level = str(config.getoption("log_cli_level") or "ERROR")
    logger = Logger(name=DESIRED_RUNNER_NAME, level=requested_log_level)
    logger.addHandler(logging.StreamHandler())

    plan_name = str(config.getoption("plan") or "default")
    logger.info(f"Selected Stochastics Plan: {plan_name}")

    config_file_path = str(config.getoption("plan_config_file"))
    logger.info(f"Loading Stochastics Config from: {config_file_path}")

    try:
        runner_config = _load_config(config_file_path)
        logger.debug(f"Loaded runner_config: {runner_config}")
    except Exception as ex:
        logger.error(f"Failed to load runner configuration: {ex}")
        config.add_cleanup(
            lambda: rich.print(
                "\n[red]Stochastic Runner not used, see error log above (look before test session starts) for details.[/red]"
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
            lambda: rich.print(
                "\n[red]Stochastic Runner not registered, see error log above (look before test session starts) for details.[/red]"
            )
        )


def _load_config(stochastics_config_path: str) -> RunnerStochasticsConfig:
    with open(stochastics_config_path) as config_file:
        raw_json = config_file.read()
        return RunnerStochasticsConfig.from_json(raw_json)  # type: ignore #TODO?

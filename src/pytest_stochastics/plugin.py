from typing import Any, Iterator, Self

import pytest
import yaml
from _pytest.nodes import Node

from .data import RunnerStochasticsConfig
from .helpers import Logger, read_git_branch


# Plugin entry point
def pytest_configure(config: pytest.Config) -> None:
    """Main entry point into the pytest plugin flow."""

    logger = Logger()
    logger.info("Configuring runner selector...")
    logger.debug(f"config.rootpath={config.rootpath}")
    logger.debug(f"config.inipath={config.inipath}")
    logger.debug(f"config.invocation_params={config.invocation_params}")

    logger.info("Acquiring current branch name...")
    branch_name = read_git_branch(logger)

    try:
        with open("pytest_config.yaml") as config_file:
            logger.info("Config file open, reading config file...")
            raw_yaml = config_file.read()
            logger.info("Read config file, parsing yaml...")
            parsed_yaml = yaml.safe_load(raw_yaml)
            logger.info("Parsed yaml, processing config...")
            runner_config = RunnerStochasticsConfig(**parsed_yaml)
            logger.info("Config created, configuring runner...")
            logger.debug(f"config={runner_config}")
            runner_selector = RunnerStochastics(runner_config, branch_name, logger)
            logger.info("Runner constructed, registering runner with pytest...")
            confirmed_name = config.pluginmanager.register(runner_selector, "stochastics_runner")
            if confirmed_name is None:
                logger.error("Failed to register `stochastics_runner` plugin!")
            logger.info(f"Registration of `{confirmed_name}` complete!")
    except Exception as ex:
        logger.error(f"Failed to configure runner: {ex}")


class RunnerStochastics:
    runner_config: RunnerStochasticsConfig
    branch: str
    lookup_test_strategy: dict[str, tuple[str, str]]  # T : (S, B)
    logger: Logger

    def __init__(self, runner_config: RunnerStochasticsConfig, current_branch: str, logger: Logger) -> None:
        self.runner_config = runner_config
        self.branch = current_branch
        self.logger = logger
        self.lookup_test_strategy = self.runner_config.gen_test_lookup(self.branch)

    def pytest_pycollect_makeitem(
        self, collector: pytest.Module | pytest.Class, name: str, obj: object
    ) -> None | pytest.Item | pytest.Collector | list[pytest.Item | pytest.Collector]:
        if not name.startswith("test_"):
            self.logger.debug(f"{name} is not a test - skipping.")
            return None

        nodeid = f"{collector.nodeid}::{name}"
        if nodeid not in self.lookup_test_strategy:
            self.logger.debug(f"No strategy found for {name}, not wrapping")
            return None

        strategy, _ = self.lookup_test_strategy[nodeid]
        strategy_config = self.runner_config.strategy_configs.get(strategy, {})
        out_of = strategy_config.get("out_of", 1)
        at_least = strategy_config.get("at_least", 1)
        self.logger.info(f"Wrapping stochastic function: `{name}` with strategy: `{strategy}`[{at_least}/{out_of}]")

        return StochasticFunction.from_parent(
            collector,
            name=name,
            obj=obj,
            strategy=strategy,
            at_least=at_least,
            out_of=out_of,
        )


class StochasticFunction(pytest.Collector):
    """Collector for stochastic tests.

    Will try to collect every test_ function by checking against its config.
    """

    obj: object
    strategy: str
    at_least: int
    out_of: int

    @classmethod
    def from_parent(cls, parent: Node, **kwargs: Any) -> Self:
        """Cooperative constructor which pytest likes, use this instead of `__init__`."""

        name = kwargs.pop("name")
        obj = kwargs.pop("obj")
        strategy = kwargs.pop("strategy")
        at_least = kwargs.pop("at_least", "")
        out_of = kwargs.pop("out_of", "")

        wrapped = super().from_parent(parent, name=name, **kwargs)  # type: ignore
        wrapped.obj = obj
        wrapped.out_of = out_of
        wrapped.at_least = at_least
        wrapped.strategy = strategy
        return wrapped

    def collect(self) -> Iterator[pytest.Item]:
        for i in range(self.out_of):
            func_name = f"{i+1:>02d} of {self.out_of:>02d}" if self.out_of > 1 else self.name
            yield pytest.Function.from_parent(self, name=func_name, callobj=self.obj)  # type: ignore

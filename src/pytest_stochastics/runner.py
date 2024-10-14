from pytest_stochastics.logger import Logger

import pytest

from pytest_stochastics.collector import StochasticFunction
from pytest_stochastics.runner_data import BranchId, RunnerStochasticsConfig, TestId, gen_fallback_lookup


class RunnerStochastics:
    def __init__(self, current_branch: str, runner_config: RunnerStochasticsConfig, logger: Logger) -> None:
        self.branch = current_branch
        self.runner_config = runner_config
        self.lookup_test_strategies = gen_fallback_lookup(runner_config, BranchId(current_branch))
        self.logger = logger

    def pytest_pycollect_makeitem(
        self, collector: pytest.Module | pytest.Class, name: str, obj: object
    ) -> None | pytest.Item | pytest.Collector | list[pytest.Item | pytest.Collector]:
        if not name.startswith("test_"):
            self.logger.debug(f"{name} is not a test - skipping.")
            return None

        nodeid = TestId(f"{collector.nodeid}::{name}")
        if nodeid not in self.lookup_test_strategies:
            self.logger.debug(f"No strategy found for {name}, not wrapping")
            return None

        test_strategy = self.lookup_test_strategies[nodeid]

        out_of = test_strategy.out_of
        at_least = test_strategy.at_least
        self.logger.info(
            f"Wrapping stochastic function: `{name}` with strategy: `{test_strategy.strategy}`[{at_least}/{out_of}]"
        )

        return StochasticFunction.from_parent(
            collector,
            name=name,
            obj=obj,
            strategy=test_strategy.strategy,
            at_least=at_least,
            out_of=out_of,
        )

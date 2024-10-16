from typing import Generator
import pytest
from _pytest.reports import TestReport
from _pytest.terminal import TerminalReporter

from pytest_stochastics.collector import StochasticFunction, StochasticFunctionCollector
from pytest_stochastics.logger import Logger
from pytest_stochastics.runner_data import PlanId, RunnerStochasticsConfig, TestId, gen_fallback_lookup


class RunnerStochastics:
    def __init__(self, current_plan: str, runner_config: RunnerStochasticsConfig, logger: Logger) -> None:
        self.plan = current_plan
        self.runner_config = runner_config
        self.lookup_test_thresholds = gen_fallback_lookup(runner_config, PlanId(current_plan))
        self.logger = logger

        self._test_tracking: dict[str, int] = {}
        self._parent_lookup: dict[str, str] = {}
        self._real_failure = False

    def pytest_pycollect_makeitem(
        self, collector: pytest.Module | pytest.Class, name: str, obj: object
    ) -> None | pytest.Item | pytest.Collector | list[pytest.Item | pytest.Collector]:
        if not name.startswith("test_"):
            self.logger.debug(f"{name} is not a test - skipping.")
            return None

        nodeid = TestId(f"{collector.nodeid}::{name}")
        if nodeid not in self.lookup_test_thresholds:
            self.logger.debug(f"No threshold found for {name}, not wrapping")
            return None

        test_threshold = self.lookup_test_thresholds[nodeid]

        out_of = test_threshold.out_of
        if out_of == 1:
            self.logger.debug(f"Redundant threshold found for {name}, not wrapping")
            return None
        
        at_least = test_threshold.at_least
        self.logger.info(
            f"Wrapping stochastic function: `{name}` with threshold: `{test_threshold.threshold}`[{at_least}/{out_of}]"
        )

        return StochasticFunctionCollector.from_parent(
            collector,
            name=name,
            obj=obj,
            threshold=test_threshold.threshold,
            at_least=at_least,
            out_of=out_of,
        )

    @pytest.hookimpl(wrapper=True)
    def pytest_runtest_protocol(
        self, item: pytest.Item, nextitem: pytest.Item | None
    ) -> Generator[None, None, bool | None]:
        if not isinstance(item, StochasticFunction) or not isinstance(item.parent, StochasticFunctionCollector):
            yield None
            return None

        key = item.parent.nodeid
        threshold = item.parent.threshold
        at_least = item.parent.at_least
        out_of = item.parent.out_of
        if key not in self._test_tracking:
            self._test_tracking[key] = at_least
            print(
                f"\n\r{"\033[94m"}StochasticSet:{"\033[0m"} {key} [{"\033[94m"}{threshold}: {at_least}/{out_of}{"\033[0m"}]",
                end="",
            )

        yield None

        if nextitem is None or item.parent != nextitem.parent:
            penalty = self._test_tracking[key]
            comment = f"{at_least - penalty} passed out of {out_of}"
            if penalty <= 0:
                outcome = f"{"\033[92m"}PASSED{"\033[0m"}"
            else:
                outcome = f"{"\033[91m"}FAILED{"\033[0m"}"
                comment += f", missing {penalty} passes"
                self._real_failure = True
            print(
                f"\n\r{"\033[94m"}StochasticSet:{"\033[0m"} {outcome} [{"\033[94m"}{comment}{"\033[0m"}]",
                end="",
            )
        return None

    def pytest_runtest_makereport(self, item: pytest.Item, call: pytest.CallInfo[None]) -> None:
        if call.when == "call":
            if item.parent is None or not isinstance(item.parent, StochasticFunctionCollector):
                return

            self._parent_lookup[item.nodeid] = item.parent.nodeid

    def pytest_runtest_logreport(self, report: TestReport) -> None:
        if report.nodeid not in self._parent_lookup:
            self._real_failure |= not report.passed
            return

        testid = self._parent_lookup[report.nodeid]
        if report.when == "call" and report.passed:
            if testid not in self._test_tracking:
                return
            self._test_tracking[testid] -= 1

    @pytest.hookimpl(tryfirst=True)
    def pytest_terminal_summary(self, terminalreporter: TerminalReporter) -> None:
        if not self._real_failure and len(self._parent_lookup) > 0:
            terminalreporter.write("\n")
            terminalreporter.write("\033[92m!!! Testing finished successfully !!!\033[0m\n")
        else:
            terminalreporter.write("\n")
            terminalreporter.write("\033[91m!!! Some tests failed. Check the details above !!!\033[0m\n")


    def pytest_sessionfinish(self, session: pytest.Session, exitstatus: int) -> None:
        if exitstatus == pytest.ExitCode.TESTS_FAILED and not self._real_failure and len(self._parent_lookup) > 0:
            session.exitstatus = pytest.ExitCode.OK

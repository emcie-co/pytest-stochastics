from logging import Logger
import rich
from typing import Sequence


import pytest
from _pytest.python import pytest_pycollect_makeitem
from _pytest.runner import runtestprotocol

from pytest_stochastics.runner_data import (
    PlanId,
    Policy,
    RunnerStochasticsConfig,
    TestId,
    gen_fallback_lookup,
)

type ItemOrCollector = pytest.Item | pytest.Collector


def annotate(
    item: ItemOrCollector,
    policy: Policy,
    attempt: int,
    logger: Logger,
) -> ItemOrCollector:
    item.originalname = item.name  # type: ignore
    attempt_id = f"[::{policy.name}#{attempt+1:02d}_of_{policy.out_of:02d}]"
    item.name += attempt_id
    item._nodeid += attempt_id  # type: ignore

    return item


class RunnerStochastics:
    """Stochastics Plugin Runner. Handles the relevant hooks."""

    def __init__(
        self,
        current_plan: str,
        runner_config: RunnerStochasticsConfig,
        logger: Logger,
    ) -> None:
        self.plan = current_plan
        self.runner_config = runner_config
        self._logger = logger

        self.lookup_test_policies = gen_fallback_lookup(runner_config, PlanId(current_plan))
        self._test_result: dict[str, list[bool]] = {}
        self._set_results: dict[str, bool] = {}
        self._did_space = False

    def pytest_pycollect_makeitem(
        self,
        collector: pytest.Module | pytest.Class,
        name: str,
        obj: object,
    ) -> None | ItemOrCollector | list[ItemOrCollector]:
        if not name.startswith("test_"):
            return None

        nodeid = TestId(f"{collector.nodeid}::{name}")
        if nodeid not in self.lookup_test_policies:
            self._logger.debug(f"No policy found for {name}, not wrapping.")
            return None

        policy = self.lookup_test_policies[nodeid]
        if policy.out_of == 1 and policy.at_least > 0:
            self._logger.debug(f"Redundant policy found for {name}, not wrapping")
            return None

        if policy.out_of <= 0:
            self._logger.debug(f"Test `{name}` disabled by configuration")
            return []

        self._logger.info(
            f"Wrapping stochastic function: `{name}` with policy: `{policy.name}`[{policy.at_least}/{policy.out_of}]"
        )

        generated: list[ItemOrCollector] = []
        transpose: list[Sequence[ItemOrCollector]] = []
        for i in range(policy.out_of):
            items: None | ItemOrCollector | list[ItemOrCollector] = pytest_pycollect_makeitem(
                collector,
                name=name,
                obj=obj,
            )
            if not items:
                continue

            if not isinstance(items, list):
                generated.append(annotate(items, policy, i, self._logger))
                continue

            for item in items:
                self.lookup_test_policies[TestId(item.nodeid)] = policy
                self._test_result[item.nodeid] = []

            transpose.append(
                list(
                    map(
                        lambda item: annotate(item, policy, i, self._logger),
                        items,
                    )
                )
            )

        if transpose:
            generated = list(
                sum(map(list, zip(*transpose)), generated),
            )

        return generated

    def pytest_runtest_protocol(
        self,
        item: pytest.Item,
        nextitem: pytest.Item | None,
    ) -> bool | None:
        item_test_id = TestId(item.nodeid.split("[::")[0])
        if item_test_id not in self._test_result:
            if item_test_id not in self._set_results:
                self._did_space = False
                return None
            return self._set_results[item_test_id]

        policy = self.lookup_test_policies[item_test_id]

        if len(self._test_result[item_test_id]) == 0:
            prefix = "\n\r" if self._did_space else "\n\r\n\r"
            rich.print(
                f"{prefix}[blue]Stochastic Set:[/blue] {item_test_id} "
                f"[[blue]{policy.name}: {policy.at_least}/{policy.out_of}[/blue]]",
                end="",
            )

        reports = runtestprotocol(item, nextitem=nextitem)
        test_passed = all(r.passed for r in reports)
        self._test_result[item_test_id].append(test_passed)

        outcome: str = ""

        results_so_far = self._test_result[item_test_id]
        passes_so_far = results_so_far.count(True)
        if policy.pass_fast and passes_so_far >= policy.at_least:
            # report.outcome = "passed"
            # report.longrepr = f"Stochastic test passed with {passes_so_far} successes"
            outcome = "[green]PASSED[/green]"

        policy_allowed_fails = policy.out_of - policy.at_least
        fails_so_far = results_so_far.count(False)
        if not outcome and (
            len(self._test_result[item_test_id]) == policy.out_of
            or (policy.fail_fast and fails_so_far > policy_allowed_fails)
        ):
            # report.outcome = "failed"
            # report.longrepr = f"Stochastic test failed with {fails_so_far} failures"
            outcome = "[red]FAILED[/red]"

        if outcome:
            comment = f"[green]{passes_so_far} pass(es) [/green][red]{fails_so_far} fail(s) [/red]"

            rich.print(f"\n\r[blue]Stochastic Result:[/blue] {outcome} [{comment}]", end="\n\r")
            self._did_space = True
            self._test_result.pop(item_test_id)
            test_passed = "FAILED" not in outcome
            self._set_results[item_test_id] = test_passed
            return test_passed

        # item.ihook.pytest_runtest_logreport(report=reports[1])

        return True

    def pytest_sessionfinish(
        self,
        session: pytest.Session,
        exitstatus: int,
    ) -> None:
        if len(self._test_result) + len(self._set_results) == 0:
            return

        if exitstatus != pytest.ExitCode.TESTS_FAILED:
            return

        if not all(v for v in self._set_results.values()):
            session.config.add_cleanup(
                lambda: rich.print(
                    "\n\r[red]Some tests failed.[/red][blue] Check the details above...[/blue]\n"
                )
            )
            return

        session.exitstatus = pytest.ExitCode.OK  # rectify the exit code
        session.config.add_cleanup(
            lambda: rich.print(
                "\n\r[green]Testing finished successfully.[/green][blue] Some stochastic tests failed[/blue][green] within acceptable margins.[/green]\n"
            )
        )

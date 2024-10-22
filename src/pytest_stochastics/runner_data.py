from dataclasses import dataclass
from typing import NewType

from dataclasses_json import dataclass_json

# Type aliases for keys
ThresholdId = NewType("ThresholdId", str)
PlanId = NewType("PlanId", str)
TestId = NewType("TestId", str)


@dataclass_json
@dataclass(frozen=True)
class ThresholdTests:
    threshold: ThresholdId
    tests: list[TestId]


@dataclass_json
@dataclass(frozen=True)
class PlanTests:
    plan: PlanId
    threshold_tests: list[ThresholdTests]


@dataclass_json
@dataclass(frozen=True)
class Threshold:
    threshold: ThresholdId
    at_least: int
    out_of: int


@dataclass_json
@dataclass(frozen=True)
class PlanFallback:
    plan: PlanId
    overrides: PlanId


@dataclass_json
@dataclass(frozen=True)
class RunnerStochasticsConfig:
    plan_tests: list[PlanTests]
    thresholds: list[Threshold]
    plan_fallbacks: list[PlanFallback]


type TestThreshold = dict[TestId, Threshold]


def gen_fallback_lookup(runner_config: RunnerStochasticsConfig, plan: PlanId) -> TestThreshold:
    """
    Based on the provided `runner_config` and `plan`,
    generates a lookup from test `nodeid` (`TestId`) to the `Threshold` resolved for that test.
    """
    result: TestThreshold = {}

    configured_plans = {bt.plan: bt.threshold_tests for bt in runner_config.plan_tests}
    fallback_plans = {fb.plan: fb.overrides for fb in runner_config.plan_fallbacks}
    thresholds = {st.threshold: st for st in runner_config.thresholds}

    plan_priorities: list[PlanId] = []
    while True:
        if plan in configured_plans:
            plan_priorities.append(plan)
        if plan not in fallback_plans:
            break
        plan = fallback_plans[plan]

    for plan in plan_priorities:
        for threshold_tests in configured_plans[plan]:
            for test in threshold_tests.tests:
                if test in result:
                    continue
                result[test] = thresholds[threshold_tests.threshold]

    return result

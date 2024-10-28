from dataclasses import dataclass, field
from typing import Any, Dict, NewType, TypeVar

from dataclasses_json import config, dataclass_json  # type: ignore

# Type aliases for keys
PolicyId = NewType("PolicyId", str)
PlanId = NewType("PlanId", str)
TestId = NewType("TestId", str)

T = TypeVar("T", PolicyId, PlanId)


def create_field_metadata(json_field_name: str, field_type: type[T]) -> Dict[str, Any]:
    """Create metadata configuration for field with alternate names"""

    def encoder(val: T) -> str:
        return str(val)

    return config(field_name=json_field_name, encoder=encoder)  # type: ignore


@dataclass_json
@dataclass(frozen=True)
class PolicyTests:
    name: PolicyId = field(metadata=create_field_metadata("policy", PolicyId))
    tests: list[TestId]


@dataclass_json
@dataclass(frozen=True)
class TestPlans:
    name: PlanId = field(metadata=create_field_metadata("plan", PlanId))
    policy_tests: list[PolicyTests]


@dataclass_json
@dataclass(frozen=True)
class Policy:
    name: PolicyId = field(metadata=create_field_metadata("policy", PolicyId))
    at_least: int
    out_of: int


@dataclass_json
@dataclass(frozen=True)
class PlanFallback:
    name: PlanId = field(metadata=create_field_metadata("plan", PlanId))
    overrides: PlanId


@dataclass_json
@dataclass(frozen=True)
class RunnerStochasticsConfig:
    test_plan_list: list[TestPlans] = field(default_factory=list)
    policy_list: list[Policy] = field(default_factory=list)
    plan_fallback_list: list[PlanFallback] = field(default_factory=list)


TestPolicy = dict[TestId, Policy]


def gen_fallback_lookup(
    runner_config: RunnerStochasticsConfig,
    plan: PlanId,
) -> TestPolicy:
    """
    Based on the provided `runner_config` and `plan`,
    generates a lookup from test `nodeid` (`TestId`) to the `Policy` resolved for that test.
    """
    result: TestPolicy = {}

    configured_plans = {bt.name: bt.policy_tests for bt in runner_config.test_plan_list}
    fallback_plans = {fb.name: fb.overrides for fb in runner_config.plan_fallback_list}
    policies = {st.name: st for st in runner_config.policy_list}

    plan_priorities: list[PlanId] = []
    while True:
        if plan in configured_plans:
            plan_priorities.append(plan)
        if plan not in fallback_plans:
            break
        plan = fallback_plans[plan]

    for plan in plan_priorities:
        for policy_tests in configured_plans[plan]:
            for test in policy_tests.tests:
                if test in result:
                    continue
                result[test] = policies[policy_tests.name]

    return result

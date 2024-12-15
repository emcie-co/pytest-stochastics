from dataclasses import dataclass, field
from dataclasses_json import config, dataclass_json  # type: ignore
import re
from typing import Any, NewType, TypeVar


# Type wrappers for keys
PolicyId = NewType("PolicyId", str)
PlanId = NewType("PlanId", str)
TestId = NewType("TestId", str)

T = TypeVar("T", PolicyId, PlanId)


def create_field_metadata(json_field_name: str, field_type: type[T]) -> dict[str, Any]:
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
class TestPlan:
    name: PlanId = field(metadata=create_field_metadata("plan", PlanId))
    policy_tests: list[PolicyTests]


@dataclass_json
@dataclass(frozen=True)
class Policy:
    name: PolicyId = field(metadata=create_field_metadata("policy", PolicyId))
    at_least: int
    out_of: int
    fail_fast: bool = True
    pass_fast: bool = True


@dataclass_json
@dataclass(frozen=True)
class PlanFallback:
    name: PlanId = field(metadata=create_field_metadata("plan", PlanId))
    overrides: PlanId


@dataclass_json
@dataclass(frozen=True)
class RunnerStochasticsConfig:
    test_plan_list: list[TestPlan] = field(default_factory=list)
    policy_list: list[Policy] = field(default_factory=list)
    plan_fallback_list: list[PlanFallback] = field(default_factory=list)


# TestPolicy = dict[TestId, Policy]
PlanPolicyTests = dict[PlanId, list[PolicyTests]]
Policies = dict[PolicyId, Policy]
PlanOverrides = dict[PlanId, PlanId]


class CompiledConfig:
    def __init__(
        self,
        runner_config: RunnerStochasticsConfig,
    ) -> None:
        self.plan_policy_tests: PlanPolicyTests = {
            bt.name: bt.policy_tests for bt in runner_config.test_plan_list
        }
        self.policies: Policies = {st.name: st for st in runner_config.policy_list}
        self.plan_overrides: PlanOverrides = {
            fb.name: fb.overrides for fb in runner_config.plan_fallback_list
        }

    def find_test_policy_id(self, plan: PlanId, test: TestId) -> PolicyId | None:
        if plan in self.plan_policy_tests:
            policy_tests = self.plan_policy_tests[plan]

            for policy in policy_tests:
                for policy_test in policy.tests:
                    if not re.match(policy_test, test):
                        continue

                    return policy.name

        if plan not in self.plan_overrides:
            return None

        return self.find_test_policy_id(self.plan_overrides[plan], test)

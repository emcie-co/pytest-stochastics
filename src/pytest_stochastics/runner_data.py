from dataclasses import dataclass
from typing import NewType

from dataclasses_json import dataclass_json

# Type aliases for keys
StrategyId = NewType("StrategyId", str)
BranchId = NewType("BranchId", str)
TestId = NewType("TestId", str)


@dataclass_json
@dataclass(frozen=True)
class StrategyTests:
    strategy: StrategyId
    tests: list[TestId]


@dataclass_json
@dataclass(frozen=True)
class BranchTests:
    branch: BranchId
    strategy_tests: list[StrategyTests]


@dataclass_json
@dataclass(frozen=True)
class Strategy:
    strategy: StrategyId
    at_least: int
    out_of: int


@dataclass_json
@dataclass(frozen=True)
class BranchFallback:
    branch: BranchId
    overrides: BranchId


@dataclass_json
@dataclass(frozen=True)
class RunnerStochasticsConfig:
    branch_tests: list[BranchTests]
    strategies: list[Strategy]
    branch_fallbacks: list[BranchFallback]


type TestStrategy = dict[TestId, Strategy]


def gen_fallback_lookup(config: RunnerStochasticsConfig, branch: BranchId) -> TestStrategy:
    result: TestStrategy = {}

    configured_branches = {bt.branch: bt.strategy_tests for bt in config.branch_tests}
    fallback_branches = {fb.branch: fb.overrides for fb in config.branch_fallbacks}
    strategies = {st.strategy: st for st in config.strategies}

    branch_priorities: list[BranchId] = []
    while True:
        if branch in configured_branches:
            branch_priorities.append(branch)
        if branch not in fallback_branches:
            break
        branch = fallback_branches[branch]

    for branch in branch_priorities:
        for strategy_tests in configured_branches[branch]:
            for test in strategy_tests.tests:
                if test in result:
                    continue
                result[test] = strategies[strategy_tests.strategy]
    return result

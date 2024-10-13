import re
from dataclasses import dataclass, field
from typing import Any, Dict, List, Tuple


@dataclass
class RunnerStochasticsConfig:
    """Object to hold the parsed configuration yaml."""

    branch_strategy_tests: Dict[str, Dict[str, List[str]]] = field(metadata={"yaml_key": "tests"})  # B : S : [T]
    strategy_configs: Dict[str, Dict[str, int]] = field(metadata={"yaml_key": "strategies"})
    branch_prototypes: Dict[str, str] = field(default_factory=dict, metadata={"yaml_key": "prototypes"})  # B: B

    def __init__(self, **kwarg_entries: Dict[str, Any]) -> None:
        for data_field in self.__dataclass_fields__.values():
            yaml_key = data_field.metadata.get("yaml_key", data_field.name)
            if yaml_key in kwarg_entries:
                setattr(self, data_field.name, kwarg_entries[yaml_key])

    def gen_test_lookup(self, branch: str) -> Dict[str, Tuple[str, str]]:
        """Transpose the strategies dict and layer them so that every test has its strategy."""

        branch_cursor = branch
        lookup: Dict[str, Tuple[str, str]] = {}
        while branch_cursor.lower() not in ("", "default"):
            branch_config = self.branch_strategy_tests.get(branch_cursor, {})
            if branch_config:
                for strat, tests in branch_config.items():
                    for test in tests:
                        test_id = re.sub(r":{1,}test_", "::test_", test)
                        if test_id not in lookup:
                            lookup[test_id] = (strat, branch_cursor)

            branch_cursor = self.branch_prototypes.get(branch_cursor, "default")
        return lookup

from pathlib import Path
from typing import Any, Iterator, Self

import pytest
from _pytest.nodes import Node

from pytest_stochastics.runner_data import Threshold


class StochasticFunctionCollector(pytest.Collector):
    """Collector for stochastic tests."""

    def __init__(
        self,
        name: str,
        threshold: Threshold,
        obj: object,
        results: list[bool] = list(),
        parent: Node | None = None,
        config: pytest.Config | None = None,
        session: pytest.Session | None = None,
        path: Path | None = None,
        nodeid: str | None = None,
    ) -> None:
        self.obj = obj
        self.threshold = threshold
        self.results = results
        super().__init__(name, parent, config, session, None, path, nodeid)

    @classmethod
    def from_parent(cls, parent: Node, **kwargs: Any) -> Self:
        """Cooperative constructor which pytest likes, use this instead of `__init__`."""

        return super().from_parent(parent, **kwargs)  # type: ignore

    def collect(self) -> Iterator[pytest.Item]:
        """Collect `out_of` copies of the function base of the strategy."""

        for i in range(self.threshold.out_of):
            func_name = f"{i+1:>02d} of {self.threshold.out_of:>02d}" if self.threshold.out_of > 1 else self.name
            yield StochasticFunction.from_parent(self, name=func_name, callobj=self.obj)  # type: ignore


class StochasticFunction(pytest.Function):
    """Marker that we wrap a `pytest.Function`."""

    pass

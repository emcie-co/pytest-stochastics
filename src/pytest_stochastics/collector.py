from typing import Any, Iterator, Self

import pytest
from _pytest.nodes import Node

from pytest_stochastics.runner_data import Threshold

class StochasticFunctionCollector(pytest.Collector):
    """Collector for stochastic tests."""

    obj: object
    threshold: Threshold
    results: list[bool]

    @classmethod
    def from_parent(cls, parent: Node, **kwargs: Any) -> Self:
        """Cooperative constructor which pytest likes, use this instead of `__init__`."""

        name = kwargs.pop("name")
        obj = kwargs.pop("obj")
        threshold = kwargs.pop("threshold")        

        wrapped = super().from_parent(parent, name=name, **kwargs)  # type: ignore
        wrapped.obj = obj        
        wrapped.threshold = threshold
        wrapped.results = []
        return wrapped

    def collect(self) -> Iterator[pytest.Item]:
        """Collect `out_of` copies of the function base of the strategy."""

        for i in range(self.threshold.out_of):
            func_name = f"{i+1:>02d} of {self.threshold.out_of:>02d}" if self.threshold.out_of > 1 else self.name
            yield StochasticFunction.from_parent(self, name=func_name, callobj=self.obj)  # type: ignore


class StochasticFunction(pytest.Function):
    """Marker that we wrap a `pytest.Function`."""

    pass

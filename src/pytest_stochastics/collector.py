from typing import Any, Iterator, Self

import pytest
from _pytest.nodes import Node


class StochasticFunctionCollector(pytest.Collector):
    """Collector for stochastic tests."""

    obj: object
    threshold: str
    at_least: int
    out_of: int
    results: list[bool]

    @classmethod
    def from_parent(cls, parent: Node, **kwargs: Any) -> Self:
        """Cooperative constructor which pytest likes, use this instead of `__init__`."""

        name = kwargs.pop("name")
        obj = kwargs.pop("obj")
        threshold = kwargs.pop("threshold")
        at_least = kwargs.pop("at_least")
        out_of = kwargs.pop("out_of")

        wrapped = super().from_parent(parent, name=name, **kwargs)  # type: ignore
        wrapped.obj = obj
        wrapped.out_of = out_of
        wrapped.at_least = at_least
        wrapped.threshold = threshold
        wrapped.results = []
        return wrapped

    def collect(self) -> Iterator[pytest.Item]:
        for i in range(self.out_of):
            func_name = f"{i+1:>02d} of {self.out_of:>02d}" if self.out_of > 1 else self.name
            yield StochasticFunction.from_parent(self, name=func_name, callobj=self.obj)  # type: ignore


class StochasticFunction(pytest.Function):
    pass

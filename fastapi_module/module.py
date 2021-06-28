from typing import Callable, Iterable, Type

from .types import CT, MT


def module(controllers: Iterable[Type[CT]]) -> Callable[[Type[MT]], Type[MT]]:
    """
    Factory function that returns a decorator converting the decorated class into a module.
    """

    def decorator(cls: Type[MT]) -> Type[MT]:
        return cls

    return decorator

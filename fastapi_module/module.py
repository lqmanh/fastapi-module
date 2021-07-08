from collections.abc import Callable
from typing import Iterable, TypeVar

from fastapi import APIRouter

from .types import InitializedError, NotAController

T = TypeVar("T")


def module(
    prefix: str = "", *, controllers: Iterable[type]
) -> Callable[[type[T]], type[T]]:
    """
    Factory function that returns a decorator converting the decorated class into a module.
    """

    def decorator(cls: type[T]) -> type[T]:
        return _module(cls, prefix, controllers=controllers)

    return decorator


def _module(cls: type[T], prefix: str = "", *, controllers: Iterable[type]) -> type[T]:
    if getattr(cls, "__fastapi_module__", False):
        raise InitializedError(cls)
    setattr(cls, "__fastapi_module__", cls.__name__)

    for controller in controllers:
        try:
            assert getattr(controller, "__fastapi_controller__")
            assert isinstance(getattr(controller, "router"), APIRouter)
        except AssertionError:
            raise NotAController(controller)

    internal_router = APIRouter(prefix=prefix)
    for controller in controllers:
        internal_router.include_router(getattr(controller, "router"))
    setattr(cls, "router", internal_router)
    return cls

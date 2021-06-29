from typing import Callable, Iterable, TypeVar

from fastapi import APIRouter

from .types import NotAController

T = TypeVar("T")


def module(*, controllers: Iterable[type]) -> Callable[[type[T]], type[T]]:
    """
    Factory function that returns a decorator converting the decorated class into a module.
    """

    def decorator(cls: type[T]) -> type[T]:
        return _module(cls, controllers)

    return decorator


def _module(cls: type[T], controllers: Iterable[type]) -> type[T]:
    if getattr(cls, "__fastapi_module__", False):
        return cls  # already initialized
    setattr(cls, "__fastapi_module__", cls.__name__)

    for controller in controllers:
        try:
            assert getattr(controller, "__fastapi_controller__")
            assert isinstance(getattr(controller, "router"), APIRouter)
        except AssertionError:
            raise NotAController(controller)

    internal_router = APIRouter()
    for controller in controllers:
        internal_router.include_router(getattr(controller, "router"))
    setattr(cls, "router", internal_router)
    return cls

from collections.abc import Callable, Sequence
from typing import Optional, TypeVar

from fastapi import APIRouter

from .types import InitializedError, NotAController

T = TypeVar("T")


def module(
    prefix: str = "", *, controllers: Sequence[type]
) -> Callable[[type[T]], type[T]]:
    """
    Factory function that returns a decorator converting the decorated class into a module.
    """

    def decorator(cls: type[T]) -> type[T]:
        return _module(cls, prefix, controllers=controllers)

    return decorator


def _module(cls: type[T], prefix: str = "", *, controllers: Sequence[type]) -> type[T]:
    if getattr(cls, "__fastapi_module__", False):
        raise InitializedError(cls)
    setattr(cls, "__fastapi_module__", cls.__name__)

    for controller in controllers:
        try:
            assert getattr(controller, "__fastapi_controller__")
        except AssertionError:
            raise NotAController(controller)

    internal_router = APIRouter()
    for controller in controllers:
        router: APIRouter = getattr(controller, "router")
        version: Optional[float] = getattr(controller, "__version__")
        if version:
            prefix = f"v{version}/{prefix.removeprefix('/')}"
        internal_router.include_router(router, prefix=prefix)
    setattr(cls, "router", internal_router)
    return cls

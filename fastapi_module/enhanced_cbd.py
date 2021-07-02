from typing import TypeVar

from .types import InitializedError
from .utils import make_cls_accept_cls_annotated_deps

T = TypeVar("T")


def enhanced_cbd(cls: type[T]) -> type[T]:
    """
    Decorator that enhances class-based dependencies.
    """
    if getattr(cls, "__fastapi_enhanced_cbd__", False):
        raise InitializedError(cls)
    setattr(cls, "__fastapi_enhanced_cbd__", cls.__name__)
    return make_cls_accept_cls_annotated_deps(cls)

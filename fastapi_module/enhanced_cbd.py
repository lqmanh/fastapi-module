from typing import Type

from .types import T
from .utils import make_cls_accept_cls_annotated_deps


def enhanced_cbd(cls: Type[T]) -> Type[T]:
    """
    Decorator that enhances class-based dependencies.
    """
    if not getattr(cls, "__fastapi_enhanced_cbd__", False):
        setattr(cls, "__fastapi_enhanced_cbd__", cls.__name__)
        cls = make_cls_accept_cls_annotated_deps(cls)
    return cls

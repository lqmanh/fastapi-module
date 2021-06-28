from typing import Type

from .types import DT
from .utils import make_cls_accept_cls_annotated_deps


def enhanced_cbd(cls: Type[DT]) -> Type[DT]:
    """
    Decorator that enhances class-based dependencies.
    """
    if getattr(cls, "__fastapi_enhanced_cbd__", False):
        return cls  # already initialized
    setattr(cls, "__fastapi_enhanced_cbd__", cls.__name__)
    return make_cls_accept_cls_annotated_deps(cls)

from typing import Type

from .types import T
from .utils import make_cls_accept_cls_annotated_deps

# special attribute to indicate a class is an enhanced class-based dependency
ENHANCED_CBD_ATTR = "__enhanced_cbd__"


def enhanced_cbd(cls: Type[T]) -> Type[T]:
    """
    Decorator that enhances class-based dependencies.
    """
    if not getattr(cls, ENHANCED_CBD_ATTR, False):
        cls = make_cls_accept_cls_annotated_deps(cls)
        setattr(cls, ENHANCED_CBD_ATTR, True)
    return cls

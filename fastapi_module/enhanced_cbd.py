from typing import Type

from .types import T
from .utils import make_cls_accept_class_attr_dep


ENHANCED_CBD_ATTR = "__enhanced_cbd_class__"


def enhanced_cbd(cls: Type[T]) -> Type[T]:
    """Enhanced class-based dependency decorator."""
    if not getattr(cls, ENHANCED_CBD_ATTR, False):
        cls = make_cls_accept_class_attr_dep(cls)
        setattr(cls, ENHANCED_CBD_ATTR, True)
    return cls

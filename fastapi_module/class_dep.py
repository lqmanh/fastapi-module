from typing import Type

from .types import T
from .utils import make_cls_accept_class_attr_dep


def class_dep(cls: Type[T]) -> Type[T]:
    """Enhanced class dependency decorator."""
    cls = make_cls_accept_class_attr_dep(cls)
    return cls

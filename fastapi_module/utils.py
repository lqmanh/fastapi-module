import inspect
from inspect import Parameter
from typing import Callable, Type, Union, get_type_hints

from pydantic.typing import is_classvar

from .types import CT, DT


def make_cls_accept_cls_annotated_deps(cls: Type[Union[CT, DT]]) -> Type[Union[CT, DT]]:
    """
    Make class `cls` accept class-annotated dependencies, performing following modifications:
    - Update `__init__` function to set any class-annotated dependencies as instance attributes
    - Update `__signature__` attribute to indicate to FastAPI what arguments should be passed to the initializer
    """
    old_init: Callable[..., None] = cls.__init__
    old_signature = inspect.signature(old_init)
    old_params = list(old_signature.parameters.values())[1:]  # drop `self` param
    new_params = [
        param
        for param in old_params
        if param.kind not in {Parameter.VAR_POSITIONAL, Parameter.VAR_KEYWORD}
    ]
    dep_names: list[str] = []
    for name, hint in get_type_hints(cls).items():
        if is_classvar(hint):
            continue
        dep_names.append(name)
        new_params.append(
            Parameter(
                name=name,
                kind=Parameter.KEYWORD_ONLY,
                annotation=hint,
                default=getattr(cls, name, Ellipsis),
            )
        )
    new_signature = old_signature.replace(parameters=new_params)

    def new_init(self: Union[CT, DT], *args, **kwargs) -> None:
        for dep_name in dep_names:
            dep_value = kwargs.pop(dep_name)
            setattr(self, dep_name, dep_value)
        old_init(self, *args, **kwargs)

    setattr(cls, "__init__", new_init)
    setattr(cls, "__signature__", new_signature)
    return cls

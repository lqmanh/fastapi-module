import inspect
from inspect import Parameter
from typing import Any, Callable, Type, TypeVar, Union, get_type_hints

from fastapi import APIRouter, Depends
from pydantic.typing import is_classvar
from starlette.routing import Route, WebSocketRoute

T = TypeVar("T")

# special attribute to indicate a class is a controller
CONTROLLER_ATTR = "__controller_class__"


def controller(router: APIRouter) -> Callable[[Type[T]], Type[T]]:
    """
    Return a decorator converting the decorated class into a controller.

    The first positional argument (typically `self`) to all methods decorated as endpoints using the provided router
    will be populated with a controller instance via FastAPI's dependency-injection system.
    """

    def decorator(cls: Type[T]) -> Type[T]:
        return _controller(router, cls)

    return decorator


def _controller(router: APIRouter, cls: Type[T]) -> Type[T]:
    """
    Replace all methods of class `cls` decorated as endpoints of router `router` with
    function calls that will properly inject an instance of class `cls`.
    """
    _init_controller(cls)
    controller_router = APIRouter()  # internal router
    function_members = inspect.getmembers(cls, inspect.isfunction)
    function_set = set(func for _, func in function_members)
    routes = [
        route
        for route in router.routes
        if isinstance(route, (Route, WebSocketRoute)) and route.endpoint in function_set
    ]
    for route in routes:
        router.routes.remove(route)
        _update_controller_route_endpoint_signature(cls, route)
        controller_router.routes.append(route)
    router.include_router(controller_router)
    return cls


def _init_controller(cls: Type[T]) -> None:
    """
    Idempotently modify class `cls`, performing following modifications:
    - `__init__` function is updated to set any class-annotated dependencies as instance attributes
    - `__signature__` attribute is updated to indicate to FastAPI what arguments should be passed to the initializer
    """
    if getattr(cls, CONTROLLER_ATTR, False):
        return  # already initialized
    old_init = cls.__init__
    old_signature = inspect.signature(old_init)
    old_params = list(old_signature.parameters.values())[1:]  # drop `self` parameter
    new_params = [
        x
        for x in old_params
        if x.kind not in {Parameter.VAR_POSITIONAL, Parameter.VAR_KEYWORD}
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

    def new_init(self: T, *args, **kwargs) -> None:
        for dep_name in dep_names:
            dep_value = kwargs.pop(dep_name)
            setattr(self, dep_name, dep_value)
        old_init(self, *args, **kwargs)

    setattr(cls, "__init__", new_init)
    setattr(cls, "__signature__", new_signature)
    setattr(cls, CONTROLLER_ATTR, True)


def _update_controller_route_endpoint_signature(
    cls: Type[T], route: Union[Route, WebSocketRoute]
) -> None:
    """
    Fix a controller route endpoint signature to ensure FastAPI injects dependencies properly.
    """
    old_endpoint = route.endpoint
    old_signature = inspect.signature(old_endpoint)
    old_params = list(old_signature.parameters.values())
    old_1st_param = old_params[0]
    new_1st_param = old_1st_param.replace(default=Depends(cls))
    new_params = [new_1st_param] + [
        param.replace(kind=Parameter.KEYWORD_ONLY) for param in old_params[1:]
    ]
    new_signature = old_signature.replace(parameters=new_params)
    setattr(route.endpoint, "__signature__", new_signature)

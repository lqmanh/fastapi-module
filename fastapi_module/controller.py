import inspect
from inspect import Parameter
from typing import Callable, Type, Union

from fastapi import APIRouter, Depends
from starlette.routing import Route, WebSocketRoute

from .types import T
from .utils import make_cls_accept_cls_annotated_deps

# special attribute to indicate a class is a controller
CONTROLLER_ATTR = "__controller_class__"


def controller(router: APIRouter) -> Callable[[Type[T]], Type[T]]:
    """
    Factory function that returns a decorator converting the decorated class into a controller.

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
    Idempotently modify class `cls`, make it accept class-annotated dependencies.
    """
    if getattr(cls, CONTROLLER_ATTR, False):
        return  # already initialized
    cls = make_cls_accept_cls_annotated_deps(cls)
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

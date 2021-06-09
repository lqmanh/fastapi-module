from typing import Any, Callable, get_type_hints

from fastapi import APIRouter


class InferringRouter(APIRouter):
    """
    Override the route decorator logic to use the annotated return type as the `response_model` if unspecified.
    """

    def add_api_route(self, path: str, endpoint: Callable[..., Any], **kwargs) -> None:
        if not kwargs.get("response_model"):
            kwargs["response_model"] = get_type_hints(endpoint).get("return")
        return super().add_api_route(path, endpoint, **kwargs)

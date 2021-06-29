from fastapi import APIRouter, FastAPI
from fastapi.testclient import TestClient
from fastapi_module import controller, module


def test_module():
    router = APIRouter()

    @controller(router)
    class TestController:
        @router.get("/", response_model=int)
        def f(self) -> int:
            return 1

    @module(controllers=[TestController])
    class TestModule:
        ...

    app = FastAPI()
    app.include_router(TestModule.router)
    client = TestClient(app)

    assert TestModule.__fastapi_module__ == "TestModule"
    assert client.get("/").text == "1"

from fastapi import APIRouter, FastAPI
from fastapi.testclient import TestClient
from fastapi_module import controller, module


def test_module():
    router = APIRouter()

    @controller(router)
    class TestController:
        @router.get("/f", response_model=int)
        def f(self) -> int:
            return 1

    @module(controllers=[TestController])
    class TestModule:
        ...

    app = FastAPI()
    app.include_router(TestModule.router)
    client = TestClient(app)

    assert TestModule.__fastapi_module__ == "TestModule"
    assert client.get("/f").text == "1"


def test_module_with_versioned_controller():
    router = APIRouter()

    @controller(router, version=1.1)
    class TestController:
        @router.get("/f", response_model=int)
        def f(self) -> int:
            return 1

    @module("/test", controllers=[TestController])
    class TestModule:
        ...

    app = FastAPI()
    app.include_router(TestModule.router)
    client = TestClient(app)

    assert client.get("/v1.1/test/f").text == "1"

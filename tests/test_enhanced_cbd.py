from typing import ClassVar

from fastapi import APIRouter, Depends
from fastapi.testclient import TestClient
from fastapi_module import enhanced_cbd


def test_enhanced_cbd():
    def dependency() -> int:
        return 1

    @enhanced_cbd
    class TestCBD:
        cx: ClassVar[int] = 1
        x: int = Depends(dependency)

        def __init__(self, y: int = Depends(dependency)):
            self.y = y

    router = APIRouter()

    @router.get("/", response_model=int)
    def get_root(fbd: int = Depends(dependency), cbd: TestCBD = Depends()) -> int:
        return fbd + cbd.x + cbd.y

    client = TestClient(router)
    assert client.get("/").text == "3"

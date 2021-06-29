from typing import Type, TypeVar

CT = TypeVar("CT")
DT = TypeVar("DT")
MT = TypeVar("MT")


class NotAController(TypeError):
    def __init__(self, cls: Type):
        self.cls = cls
        super().__init__()

    def __str__(self) -> str:
        return f"{self.cls} is not a controller class"

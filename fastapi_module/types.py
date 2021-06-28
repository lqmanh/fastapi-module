from typing import ClassVar, Protocol, TypeVar, runtime_checkable

T = TypeVar("T")


@runtime_checkable
class Controller(Protocol):
    __fastapi_controller__: ClassVar[str]


@runtime_checkable
class EnhancedCBD(Protocol):
    __fastapi_enhanced_cbd__: ClassVar[str]


@runtime_checkable
class Module(Protocol):
    __fastapi_module__: ClassVar[str]

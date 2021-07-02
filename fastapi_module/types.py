class InitializedError(Exception):
    def __init__(self, cls: type):
        self.cls = cls
        super().__init__()

    def __str__(self) -> str:
        return f"{self.cls} has already been initialized"


class NotAController(TypeError):
    def __init__(self, cls: type):
        self.cls = cls
        super().__init__()

    def __str__(self) -> str:
        return f"{self.cls} is not a controller class"

from typing import TYPE_CHECKING
from callables import ZSDCallable, ZSDFunction
from output import ZSDRuntimeError
from zsdtoken import Token

if TYPE_CHECKING:
    from interpreter import Interpreter

class ZSDClass(ZSDCallable):
    def __init__(self, name: str, methods: dict[str, ZSDFunction]) -> None:
        self.name = name
        self.methods = methods

    def find_method(self, name: str):
        return self.methods.get(name, None)

    def arity(self) -> int:
        init = self.find_method("init")
        if init:
            return init.arity()
        return 0

    def call(self, interpreter: "Interpreter", arguments: list[object]) -> object:
        instance = ZSDInstance(self)

        initializer = self.find_method("init")
        if initializer:
            initializer.bind(instance).call(interpreter, arguments)

        return instance

    def __repr__(self) -> str:
        return f"<class {self.name}>"
    
class ZSDInstance:
    def __init__(self, klass: ZSDClass) -> None:
        self.klass = klass
        self.fields: dict[str, object] = {}

    def get(self, name: Token):
        if name.lexeme in self.fields:
            return self.fields[name.lexeme]
        
        method = self.klass.find_method(name.lexeme)
        if method:
            return method.bind(self)
        
        raise ZSDRuntimeError(name, f"Undefined attribute {name.lexeme!r}.")
    
    def set(self, name: Token, value: object):
        self.fields[name.lexeme] = value

    def __repr__(self) -> str:
        return f"<{self.klass.name} object>"
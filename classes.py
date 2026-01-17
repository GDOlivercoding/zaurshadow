from __future__ import annotations
from typing import TYPE_CHECKING
from callables import ZSDCallable, ZSDFunction, ZSDNativeFunction
from output import ZSDRuntimeError
from zsdtoken import Token

if TYPE_CHECKING:
    from interpreter import Interpreter

class ZSDObject:
    def __init__(self, klass: ZSDClass) -> None:
        self.klass = klass
        self.fields: dict[str, object] = {
            # the class that this instance is of
            "__class__": self.klass,
            "init": self.klass.find_method("init")
        }

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


class ZSDClass(ZSDCallable, ZSDObject):
    def __init__(self, name: str, methods: dict[str, ZSDFunction], superclass: ZSDClass | None = None) -> None:
        self.name = name
        self.methods = methods
        self.superclass = superclass
        super().__init__(self)

    def find_method(self, name: str) -> ZSDFunction | None:
        method = self.methods.get(name)
        if method:
            return method
        
        return self.superclass and self.superclass.find_method(name)

    def arity(self):
        init = self.find_method("init")
        if init:
            return init.arity()
        return (0, 0)

    def call(self, interpreter: Interpreter, arguments: list[object]) -> object:
        instance = ZSDObject(self)

        initializer = self.find_method("init")
        if initializer:
            initializer.bind(instance).call(interpreter, arguments)

        return instance

    def __repr__(self) -> str:
        return f"<class {self.name}>"
    
class ZSDInt(ZSDClass):
    def __init__(self, name: str, methods: dict[str, ZSDFunction], superclass: ZSDClass | None = None) -> None:
        super().__init__(name, methods, superclass)
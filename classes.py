from __future__ import annotations
from collections.abc import Mapping
from typing import TYPE_CHECKING, Any
from callables import ZSDCallable, ZSDFunction, ZSDNativeFunction
from output import ZSDRuntimeError
from zsdtoken import Token

if TYPE_CHECKING:
    from interpreter import Interpreter

class ZSDObject:
    def __init__(self, klass: ZSDClass, fields: dict[str, Any] | None = None) -> None:
        self.klass = klass
        self.fields: dict[str, Any] = {"__class__": klass} | (fields or {})

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
    def __init__(
        self, 
        name: str, 
        methods: Mapping[str, ZSDFunction], 
        superclass: ZSDClass | None = None,
        is_type_class: bool = False
    ) -> None:
        super().__init__(self)
        self.name = name
        self.methods = methods
        # The superclass of a class on top is the object class
        self.superclass = None if is_type_class else superclass or ZSDType
        if not is_type_class:
            # A class instance will always be an instance of the class type
            self.fields["__class__"] = ZSDType

    def find_method(self, name: str) -> ZSDFunction | None:
        method = self.methods.get(name)
        if method:
            return method
        
        if self.superclass and self is not self.superclass:
            return self.superclass.find_method(name)
        
    def get(self, name: Token):
        if name.lexeme in self.fields:
            return self.fields[name.lexeme]
        
        method = self.find_method(name.lexeme)
        if method:
            return method
        
        raise ZSDRuntimeError(name, f"Undefined attribute {name.lexeme!r}.")

    def arity(self):
        init = self.find_method("init")
        if init:
            return init.arity()
        return (0, 0)

    def call(self, interpreter: Interpreter, arguments: list[object]) -> object:
        init = self.find_method("init")
        if init is None:
            # I'm going to use this global as a marker
            return NotImplemented
        
        instance = ZSDObject(self)
        init.bind(instance).call(interpreter, arguments)

        return instance

    def __repr__(self) -> str:
        return f"<class {self.name}>"
    
ZSDType = ZSDClass(
    "type", 
    {
        "init": ZSDNativeFunction((0, 0), "init", lambda self: None)
    },
    None,
    True
)
ZSDType.fields["__class__"] = ZSDType
    
class ZSDNativeClass(ZSDClass):
    def __init__(
        self, 
        name: str, 
        init: ZSDNativeFunction, 
        methods: dict[str, ZSDNativeFunction], 
        superclass: ZSDClass | None = None
    ) -> None:
        super().__init__(name, methods, superclass)
        self.name = name
        self.init = init
        self.methods = methods | {init.name: init}
        self.superclass = superclass

    def arity(self):
        return self.init.arity()
    
    def find_method(self, name: str): 
        method = self.methods.get(name)
        if method:
            return method
        
        if self.superclass and self is not self.superclass:
            return self.superclass.find_method(name)

    def call(self, interpreter: Interpreter, arguments: list[object]) -> ZSDObject:
        instance = ZSDObject(self)
        self.init.bind(instance).call(interpreter, arguments)
        return instance
    
    def __repr__(self) -> str:
        return f"<native class {self.name}>"
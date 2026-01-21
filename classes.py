from __future__ import annotations
from functools import partial
from typing import TYPE_CHECKING, Any
from callables import ZSDCallable, ZSDFunction, ZSDNativeFunction
from output import ZSDRuntimeError
from zsdtoken import Token
from literals import nil

if TYPE_CHECKING:
    from interpreter import Interpreter

class ZSDObject:
    def __init__(self, klass: ZSDClass) -> None:
        self.klass = klass
        self.fields: dict[str, Any] = {
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
    
class ZSDNativeClass(ZSDClass):
    def __init__(
        self, 
        name: str, 
        init: ZSDNativeFunction, 
        methods: dict[str, ZSDNativeFunction], 
        superclass: ZSDClass | None = None
    ) -> None:
        self.name = name
        self.init = init
        self.methods = methods | {init.name: init}
        self.superclass = superclass

    def arity(self):
        return self.init.arity()
    
    def find_method(self, name: str): # type: ignore
        method = self.methods.get(name)
        if method:
            return method
        
        return self.superclass and self.superclass.find_method(name)

    def call(self, interpreter: Interpreter, arguments: list[object]) -> object:
        return self.init.call(interpreter, [ZSDObject(self)] + arguments)
    
    def __repr__(self) -> str:
        return f"<native class {self.name}>"

# region native code

def range_init(inter: Interpreter, arguments: list[Any]):
    self: ZSDObject = arguments.pop(0)

    start = stop = 0
    step = 1

    match len(arguments):
        case 1:
            stop, = arguments
        case 2:
            start, stop = arguments
        case 3:
            start, stop, step = arguments

    self.fields["start"] = start
    self.fields["stop"] = stop
    self.fields["step"] = step
    self.fields["index"] = 0
    return self

def range_iter(inter: Interpreter, arguments: list[Any]):
    return arguments[0]

def range_next(inter: Interpreter, arguments: list[Any]):
    self: ZSDObject = arguments.pop(0)

    start: int = self.fields["start"]
    stop: int = self.fields["stop"]
    step: int = self.fields["step"]
    index: int = self.fields["index"]

    next_value = start + (index * step)
    if next_value >= stop:
        self.fields["index"] = 0
        return nil
    
    self.fields["index"] = index + 1
    return next_value

methods = {
    "iter": ZSDNativeFunction((0, 0), "iter", range_iter),
    "next": ZSDNativeFunction((0, 0), "next", range_next)
}

range_class = ZSDNativeClass(
    "range", 
    ZSDNativeFunction((1, 3), "init", range_init),
    methods
)
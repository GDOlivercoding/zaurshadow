from __future__ import annotations
from itertools import chain
import time
from typing import TYPE_CHECKING, Any
from classes import ZSDClass, ZSDNativeClass, ZSDObject, ZSDType
from literals import ZSDStopIteration, nil
from callables import ZSDFunction, ZSDNativeFunction
from output import ZSDRuntimeError
from zsdtoken import Token

if TYPE_CHECKING:
    from interpreter import Interpreter

elements: list[ZSDFunction | ZSDClass] = []
_interpreter = None

def range_init(self: ZSDObject, *arguments: int):
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

def range_next(self: ZSDObject):
    start: int = self.fields["start"]
    stop: int = self.fields["stop"]
    step: int = self.fields["step"]
    # TODO: Make an Iterable and Iterator type
    index: int = self.fields["index"]

    next_value = start + (index * step)
    if next_value >= stop:
        self.fields["index"] = 0
        return ZSDStopIteration
    
    self.fields["index"] = index + 1
    return next_value

methods = {
    "next": ZSDNativeFunction((0, 0), "next", range_next)
}

range_class = ZSDNativeClass(
    "range", 
    ZSDNativeFunction((1, 3), "init", range_init),
    methods
)
elements.append(range_class)

def int_init(self, value = 0):
    self.fields["value"] = int(value)

int_class = ZSDNativeClass(
    "int",
    ZSDNativeFunction((0, 1), "init", int_init),
    {}
)
elements.append(int_class)

clock = ZSDNativeFunction((0, 0), "clock", lambda: float(format(time.perf_counter(), ".3f")))
elements.append(clock)

def to_string_callback(value = ""):
    return str(value)

to_string = ZSDNativeFunction((0, 1), "str", to_string_callback)
elements.append(to_string)

class ZSDAnonObject(ZSDObject):
    def __init__(self, attributes: dict[str, Any], methods: dict[str, ZSDFunction]) -> None:
        super().__init__(ZSDType, attributes)
        self.fields["__class__"] = nil
        self.methods = methods
        # XXX Dangerous, but the only method we will ever want is .find_method()
        setattr(self, "klass", self)

    def get(self, name: Token):
        if name.lexeme in self.fields:
            return self.fields[name.lexeme]
        
        method = self.find_method(name.lexeme)
        if method:
            return method.bind(self)
        
        raise ZSDRuntimeError(name, f"Undefined attribute {name.lexeme!r}.")
    
    def find_method(self, name: str):
        return self.methods.get(name)
        
    def __repr__(self) -> str:
        # TODO Make less verbose
        # Methods should display as meth(param1, param2)
        # <Object name='mreow' init() get(name)>
        attributes = "".join([
            f" {name}={value!r}"
            for name, value in chain(self.fields.items(), self.methods.items())
            if not name.startswith("_")
        ])
        return f"<Object{attributes}>"
    
# region meta

def inject(interpreter: Interpreter):
    global _interpreter
    _interpreter = interpreter
    for elem in elements:
        interpreter.globals.define(elem.name, elem)

def request_interpreter():
    if _interpreter is None:
        raise ValueError("Attempted to access interpreter before initialization.")
    return _interpreter
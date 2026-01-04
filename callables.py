from __future__ import annotations
from abc import ABC, abstractmethod
from collections.abc import Callable
import time
from typing import TYPE_CHECKING
from environment import Environment
from output import ReturnException
import stmt

if TYPE_CHECKING:
    from interpreter import Interpreter

class ZSDCallable(ABC):
    @abstractmethod
    def call(self, interpreter: Interpreter, arguments: list[object]) -> object: ...
    @abstractmethod
    def arity(self) -> int: ...

class ZSDFunction(ZSDCallable):
    def __init__(self, declaration: stmt.Function, closure: Environment) -> None:
        self.declaration = declaration
        self.closure = closure

    def arity(self) -> int:
        return len(self.declaration.params)

    def call(self, interpreter: Interpreter, arguments: list[object]) -> object:
        env = Environment(self.closure)

        for param, arg in zip(self.declaration.params, arguments):
            env.define(param.lexeme, arg)

        try:
            interpreter.execute_block(self.declaration.body, env)
        except ReturnException as exc:
            return exc.value

    def __repr__(self) -> str:
        decl = self.declaration
        params = [param.lexeme for param in decl.params]

        if len(params) > 9:
            params = params[:9] + ["..."]

        return f"<function {decl.name.lexeme}({", ".join(params)})>"

class ZSDNativeFunction(ZSDCallable):
    def __init__(self, arity: int, name: str, callable: Callable[[Interpreter, list[object]], object]) -> None:
        self._arity = arity
        self.name = name
        self.callable = callable

    def arity(self) -> int:
        return self._arity
    
    def call(self, interpreter: Interpreter, arguments: list[object]) -> object:
        return self.callable(interpreter, arguments)
    
    def __repr__(self) -> str:
        return f"<native {self.name}()>"
    
clock = ZSDNativeFunction(0, "clock", lambda i, a: time.perf_counter())
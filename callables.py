from __future__ import annotations
from abc import ABC, abstractmethod
from collections.abc import Callable
from dataclasses import dataclass
from itertools import zip_longest
from typing import TYPE_CHECKING
from environment import Environment
from output import ReturnException, ZSDRuntimeError
import stmt
from zsdtoken import Token
from literals import nil

if TYPE_CHECKING:
    from interpreter import Interpreter
    from classes import ZSDObject

class ZSDCallable(ABC):
    @abstractmethod
    def call(self, interpreter: Interpreter, arguments: list[object]) -> object: ...
    @abstractmethod
    def arity(self) -> tuple[int, int]: 
        """Minimal and maximal arity in (min_args, max_args) form"""

@dataclass
class ZSDParam:
    name: Token
    default: object | None

class ZSDFunction(ZSDCallable):
    def __init__(self, declaration: stmt.Function, parameters: list[ZSDParam], closure: Environment, is_init: bool = False) -> None:
        self.declaration = declaration
        self.parameters = parameters
        self.closure = closure
        self.is_init = is_init
        self.name = "function"

    def arity(self):
        try:
            index = [p.default for p in self.parameters].index(None)
        except ValueError:
            index = -1

        return (
            index + 1,
            len(self.parameters)
        )

    def call(self, interpreter: Interpreter, arguments: list[object]) -> object:
        env = Environment(self.closure)

        # I assume here, that len(arguments) <= len(self.parameters)
        # and that len(arguments) >= required arguments
        for param, arg in zip_longest(self.parameters, arguments, fillvalue=None):
            assert param is not None # can never be None

            if arg is None:
                # param.default must not be of type None
                # because we receive >= the amount of required arguments
                arg = param.default

            env.define(param.name.lexeme, arg)

        try:
            interpreter.execute_block(self.declaration.body, env)
        except ReturnException as exc:
            if self.is_init:
                if exc.value is not nil:
                    raise ZSDRuntimeError(exc.return_stmt.keyword, "Cannot return value from initializer.")
                return self.closure.get_at("this", 0)

            return exc.value
        
        if self.is_init: 
            return self.closure.get_at("this", 0)
        
        return nil
        
    def bind(self, instance: "ZSDObject"):
        env = Environment(self.closure)
        env.define("this", instance)
        self.name = "bound method"
        return type(self)(self.declaration, self.parameters, env)

    def __repr__(self) -> str:
        decl = self.declaration
        params = [param.name.lexeme for param in decl.params]

        if len(params) > 9:
            params = params[:9] + ["..."]

        return f"<{self.name} {decl.name.lexeme}({", ".join(params)})>"

class ZSDNativeFunction(ZSDCallable):
    def __init__(
        self, 
        arity: tuple[int, int], 
        name: str, 
        callable: Callable[[Interpreter, list[object]], object],
        binding: "ZSDObject | None" = None
    ) -> None:
        self._arity = arity
        self.name = name
        self.callable = callable
        self.binding = binding

    def bind(self, instance: "ZSDObject"):
        return type(self)(self._arity, self.name, self.callable, instance)

    def arity(self):
        return self._arity
    
    def call(self, interpreter: Interpreter, arguments: list[object]) -> object:
        if self.binding:
            arguments = [self.binding] + arguments

        return self.callable(interpreter, arguments)
    
    def __repr__(self) -> str:
        return f"<native {self.name}()>"

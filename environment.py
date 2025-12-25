from __future__ import annotations
from output import ZSDRuntimeError
from zsdtoken import Token

class Environment:
    def __init__(self, enclosing: Environment | None = None) -> None:
        self.enclosing = enclosing
        self.values: dict[str, object] = {}

    def get(self, name: Token):
        if name.lexeme in self.values:
            return self.values[name.lexeme]
        
        if self.enclosing: 
            return self.enclosing.get(name)
        
        raise ZSDRuntimeError(name, f"Undefined variable {name.lexeme!r}.")

    def define(self, name: str, value: object):
        self.values[name] = value

    def assign(self, name: Token, value: object):
        if name.lexeme in self.values:
            self.values[name.lexeme] = value
            return
        
        if self.enclosing:
            return self.enclosing.assign(name, value)
        
        raise ZSDRuntimeError(name, f"Undefined variable {name.lexeme!r}.")
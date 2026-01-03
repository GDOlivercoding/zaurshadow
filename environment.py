from __future__ import annotations
from output import ZSDRuntimeError
from zsdtoken import Token

class Environment:
    def __init__(self, parent_scope: Environment | None = None) -> None:
        self.parent_scope = parent_scope
        self.values: dict[str, object] = {}

    # ... = a;
    def get(self, name: Token, distance: int | None = None):
        if distance is not None:
            return self.ancestor(distance).values[name.lexeme]

        if name.lexeme in self.values:
            return self.values[name.lexeme]
        
        if self.parent_scope: 
            return self.parent_scope.get(name)
        
        raise ZSDRuntimeError(name, f"Undefined variable {name.lexeme!r}.")

    # make it impossible to redefine a variable later
    # var a  = ...;
    def define(self, name: str, value: object):
        self.values[name] = value

    def ancestor(self, distance: int):
        env = self

        for i in range(distance):
            if not env.parent_scope:
                raise RuntimeError(
                    f"Internal: Cannot reach scope depth distance of {distance},"
                    f" stopped at depth {i} at env {env} from env {self}."
            )
            env = env.parent_scope

        return env

    # a = ...;
    def assign(self, name: Token, value: object, distance: int | None = None):
        if distance is not None:
            self.ancestor(distance).values[name.lexeme] = value

        if name.lexeme in self.values:
            self.values[name.lexeme] = value
            return
        
        if self.parent_scope:
            return self.parent_scope.assign(name, value)
        
        raise ZSDRuntimeError(name, f"Undefined variable {name.lexeme!r}.")
    
    def __repr__(self) -> str:
        return f"<{self.__class__.__name__} parent={self.parent_scope} values={self.values}>"
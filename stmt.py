from __future__ import annotations
from abc import ABC
from dataclasses import dataclass
from functools import partial
from types import MethodType
from typing import TYPE_CHECKING, Protocol
from expr import Expr, Variable
from zsdtoken import Token

if TYPE_CHECKING:
    norepr_dataclass = dataclass
else:
    norepr_dataclass = partial(dataclass, repr=False)

class Visitor[T](Protocol):
    def visit_expression_stmt(self, stmt: Expression) -> T: ...
    def visit_function_stmt(self, stmt: Function) -> T: ...
    def visit_if_stmt(self, stmt: If) -> T: ...
    def visit_block_stmt(self, stmt: Block) -> T: ...
    def visit_class_stmt(self, stmt: Class) -> T: ...
    def visit_print_stmt(self, stmt: Print) -> T: ...
    def visit_return_stmt(self, stmt: Return) -> T: ...
    def visit_var_stmt(self, stmt: Var) -> T: ...
    def visit_while_stmt(self, stmt: While) -> T: ...
    def visit_for_stmt(self, stmt: For) -> T: ...

class Stmt(ABC): 
    def accept[T](self, visitor: Visitor[T]) -> T: 
        return getattr(visitor, f"visit_{type(self).__name__.lower()}_stmt")(self)
    
    def __repr__(self) -> str:
        attributes = "".join([
            f" {name}={attr!r}"
            for name in dir(self) 
            if not name.startswith("_")
            and not isinstance(attr := getattr(self, name), MethodType)
        ])
        return f"<{self.__class__.__name__}{attributes}>"

@norepr_dataclass
class Expression(Stmt):
    expression: Expr

@norepr_dataclass
class Param:
    name: Token
    default: Expr | None

@norepr_dataclass
class Function(Stmt):
    name: Token
    params: list[Param]
    body: Block

@norepr_dataclass
class If(Stmt):
    conditions: list[tuple[Expr, Stmt]]
    else_branch: Stmt | None = None

@norepr_dataclass
class Block(Stmt):
    statements: list[Stmt]

@norepr_dataclass
class Class(Stmt):
    name: Token
    methods: list[Function]
    superclass: Variable | None = None

@norepr_dataclass
class Print(Stmt):
    expression: Expr

@norepr_dataclass
class Return(Stmt):
    keyword: Token
    value: Expr

@norepr_dataclass
class Var(Stmt):
    name: Token
    initializer: Expr

@norepr_dataclass
class While(Stmt):
    condition: Expr
    body: Stmt

@norepr_dataclass
class For(Stmt):
    keyword: Token
    iter_var: Token
    iterable: Expr
    body: Stmt
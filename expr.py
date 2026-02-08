from __future__ import annotations
from types import MethodType
from typing import TYPE_CHECKING
from typing import Protocol
from zsdtoken import Token
from dataclasses import dataclass
from functools import partial


if TYPE_CHECKING:
    from stmt import Function
    norepr_dataclass = dataclass
else:
    norepr_dataclass = partial(dataclass, repr=False)

class Visitor[T](Protocol):
    def visit_assign_expr(self, expr: Assign) -> T: ...
    def visit_binary_expr(self, expr: Binary) -> T: ...
    def visit_call_expr(self, expr: Call) -> T: ...
    def visit_get_expr(self, expr: Get) -> T: ...
    def visit_set_expr(self, expr: Set) -> T: ...
    def visit_super_expr(self, expr: Super) -> T: ...
    def visit_this_expr(self, expr: This) -> T: ...
    def visit_grouping_expr(self, expr: Grouping) -> T: ...
    def visit_logical_expr(self, expr: Logical) -> T: ...
    def visit_literalvalue_expr(self, expr: LiteralValue) -> T: ...
    def visit_unary_expr(self, expr: Unary) -> T: ...
    def visit_variable_expr(self, expr: Variable) -> T: ...
    def visit_range_expr(self, expr: Range) -> T: ...
    def visit_anonobject_expr(self, expr: AnonObject) -> T: ...
    def visit_instanceof_expr(self, expr: InstanceOf) -> T: ...
 
class Expr: 
    def accept[T](self, visitor: Visitor[T]) -> T: 
        return getattr(visitor, f"visit_{type(self).__name__.lower()}_expr")(self)
    
    def __repr__(self) -> str:
        attributes = "".join([
            f" {name}={attr!r}"
            for name in dir(self) 
            if not name.startswith("_")
            and not isinstance(attr := getattr(self, name), MethodType)
        ])
        return f"<{self.__class__.__name__}{attributes}>"

@norepr_dataclass
class Assign(Expr):
    name: Token
    value: Expr

@norepr_dataclass
class Binary(Expr):
    left: Expr
    operator: Token
    right: Expr

@norepr_dataclass
class Call(Expr):
    callee: Expr
    paren: Token
    arguments: list[Expr]

@norepr_dataclass
class Get(Expr):
    object: Expr
    name: Token

@norepr_dataclass
class Set(Expr):
    object: Expr
    name: Token
    value: Expr

@norepr_dataclass
class Super(Expr):
    keyword: Token
    method: Token

@norepr_dataclass
class This(Expr):
    keyword: Token

@norepr_dataclass
class Grouping(Expr):
    expression: Expr

@norepr_dataclass
class Logical(Expr):
    left: Expr
    operator: Token
    right: Expr

# 'Literal' collides with typing.Literal
@norepr_dataclass
class LiteralValue(Expr):
    value: object

@norepr_dataclass
class Unary(Expr):
    operator: Token
    right: Expr

@norepr_dataclass
class Variable(Expr):
    name: Token

@norepr_dataclass
class Range(Expr):
    start: int
    stop: int
    
@norepr_dataclass
class AnonObject(Expr):
    attributes: dict[Token, Expr]
    methods: dict[str, Function]
    
@norepr_dataclass
class InstanceOf(Expr):
    left: Expr | None
    keyword: Token
    right: Expr
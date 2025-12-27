from __future__ import annotations
from abc import ABC, abstractmethod
from typing import Protocol
from zsdtoken import Token

class Visitor[T](Protocol):
    def visit_assign_expr(self, expr: Assign) -> T: ...
    def visit_binary_expr(self, expr: Binary) -> T: ...
    def visit_grouping_expr(self, expr: Grouping) -> T: ...
    def visit_logical_expr(self, expr: Logical) -> T: ...
    def visit_literalvalue_expr(self, expr: LiteralValue) -> T: ...
    def visit_unary_expr(self, expr: Unary) -> T: ...
    def visit_variable_expr(self, expr: Variable) -> T: ...

class Expr(ABC): 
    @abstractmethod
    def accept[T](self, visitor: Visitor[T]) -> T: ...


class Assign(Expr):
    def __init__(self, name: Token, value: Expr):
        self.name = name
        self.value = value

    def accept[T](self, visitor: Visitor[T]) -> T:
        return visitor.visit_assign_expr(self)


class Binary(Expr):
    def __init__(self, left: Expr, operator: Token, right: Expr):
        self.left = left
        self.operator = operator
        self.right = right

    def accept[T](self, visitor: Visitor[T]) -> T:
        return visitor.visit_binary_expr(self)


class Grouping(Expr):
    def __init__(self, expression: Expr):
        self.expression = expression

    def accept[T](self, visitor: Visitor[T]) -> T:
        return visitor.visit_grouping_expr(self)


class Logical(Expr):
    def __init__(self, left: Expr, operator: Token, right: Expr):
        self.left = left
        self.operator = operator
        self.right = right

    def accept[T](self, visitor: Visitor[T]) -> T:
        return visitor.visit_logical_expr(self)


class LiteralValue(Expr):
    def __init__(self, value: object):
        self.value = value

    def accept[T](self, visitor: Visitor[T]) -> T:
        return visitor.visit_literalvalue_expr(self)


class Unary(Expr):
    def __init__(self, operator: Token, right: Expr):
        self.operator = operator
        self.right = right

    def accept[T](self, visitor: Visitor[T]) -> T:
        return visitor.visit_unary_expr(self)


class Variable(Expr):
    def __init__(self, name: Token):
        self.name = name

    def accept[T](self, visitor: Visitor[T]) -> T:
        return visitor.visit_variable_expr(self)


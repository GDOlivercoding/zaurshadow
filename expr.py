from __future__ import annotations
from abc import ABC, abstractmethod
from typing import Protocol
from zsdtoken import Token

class Visitor[T](Protocol):
    def visit_binary_expr(self, expr: Binary) -> T: ...
    def visit_grouping_expr(self, expr: Grouping) -> T: ...
    def visit_literal_expr(self, expr: LiteralValue) -> T: ...
    def visit_unary_expr(self, expr: Unary) -> T: ...

class Expr(ABC): 
    @abstractmethod
    def accept[T](self, visitor: Visitor[T]) -> T: ...

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
    
# 'Literal' collides with typing.Literal
class LiteralValue(Expr):
    def __init__(self, value: object):
        self.value = value

    def accept[T](self, visitor: Visitor[T]) -> T:
        return visitor.visit_literal_expr(self)
    
class Unary(Expr):
    def __init__(self, operator: Token, right: Expr):
        self.operator = operator
        self.right = right

    def accept[T](self, visitor: Visitor[T]) -> T:
        return visitor.visit_unary_expr(self)

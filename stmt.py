from __future__ import annotations
from abc import ABC, abstractmethod
from typing import Protocol
from expr import Expr
from zsdtoken import Token

class Visitor[T](Protocol):
    def visit_expression_stmt(self, stmt: Expression) -> T: ...
    def visit_if_stmt(self, stmt: If) -> T: ...
    def visit_block_stmt(self, stmt: Block) -> T: ...
    def visit_print_stmt(self, stmt: Print) -> T: ...
    def visit_var_stmt(self, stmt: Var) -> T: ...

class Stmt(ABC): 
    @abstractmethod
    def accept[T](self, visitor: Visitor[T]) -> T: ...


class Expression(Stmt):
    def __init__(self, expression: Expr):
        self.expression = expression

    def accept[T](self, visitor: Visitor[T]) -> T:
        return visitor.visit_expression_stmt(self)


class If(Stmt):
    def __init__(self, conditions: list[tuple[Expr, Stmt]], else_branch: Stmt | None = None):
        self.conditions = conditions
        self.else_branch = else_branch

    def accept[T](self, visitor: Visitor[T]) -> T:
        return visitor.visit_if_stmt(self)


class Block(Stmt):
    def __init__(self, statements: list[Stmt]):
        self.statements = statements

    def accept[T](self, visitor: Visitor[T]) -> T:
        return visitor.visit_block_stmt(self)


class Print(Stmt):
    def __init__(self, expression: Expr):
        self.expression = expression

    def accept[T](self, visitor: Visitor[T]) -> T:
        return visitor.visit_print_stmt(self)


class Var(Stmt):
    def __init__(self, name: Token, initializer: Expr):
        self.name = name
        self.initializer = initializer

    def accept[T](self, visitor: Visitor[T]) -> T:
        return visitor.visit_var_stmt(self)


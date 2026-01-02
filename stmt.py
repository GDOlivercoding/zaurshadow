from __future__ import annotations
from abc import ABC, abstractmethod
from typing import Protocol
from expr import Expr
from zsdtoken import Token

class Visitor[T](Protocol):
    def visit_expression_stmt(self, stmt: Expression) -> T: ...
    def visit_function_stmt(self, stmt: Function) -> T: ...
    def visit_if_stmt(self, stmt: If) -> T: ...
    def visit_block_stmt(self, stmt: Block) -> T: ...
    def visit_print_stmt(self, stmt: Print) -> T: ...
    def visit_return_stmt(self, stmt: Return) -> T: ...
    def visit_var_stmt(self, stmt: Var) -> T: ...
    def visit_while_stmt(self, stmt: While) -> T: ...

class Stmt(ABC): 
    @abstractmethod
    def accept[T](self, visitor: Visitor[T]) -> T: ...


class Expression(Stmt):
    def __init__(self, expression: Expr):
        self.expression = expression

    def accept[T](self, visitor: Visitor[T]) -> T:
        return visitor.visit_expression_stmt(self)

    def __repr__(self) -> str:
        return f"<Expression expression={self.expression}>"

class Function(Stmt):
    def __init__(self, name: Token, params: list[Token], body: list[Stmt]):
        self.name = name
        self.params = params
        self.body = body

    def accept[T](self, visitor: Visitor[T]) -> T:
        return visitor.visit_function_stmt(self)

    def __repr__(self) -> str:
        return f"<Function name={self.name} params={self.params} body={self.body}>"

class If(Stmt):
    def __init__(self, conditions: list[tuple[Expr, Stmt]], else_branch: Stmt | None = None):
        self.conditions = conditions
        self.else_branch = else_branch

    def accept[T](self, visitor: Visitor[T]) -> T:
        return visitor.visit_if_stmt(self)

    def __repr__(self) -> str:
        return f"<If conditions={self.conditions} else_branch={self.else_branch}>"

class Block(Stmt):
    def __init__(self, statements: list[Stmt]):
        self.statements = statements

    def accept[T](self, visitor: Visitor[T]) -> T:
        return visitor.visit_block_stmt(self)

    def __repr__(self) -> str:
        return f"<Block statements={self.statements}>"

class Print(Stmt):
    def __init__(self, expression: Expr):
        self.expression = expression

    def accept[T](self, visitor: Visitor[T]) -> T:
        return visitor.visit_print_stmt(self)

    def __repr__(self) -> str:
        return f"<Print expression={self.expression}>"

class Return(Stmt):
    def __init__(self, keyword: Token, value: Expr):
        self.keyword = keyword
        self.value = value

    def accept[T](self, visitor: Visitor[T]) -> T:
        return visitor.visit_return_stmt(self)

    def __repr__(self) -> str:
        return f"<Return keyword={self.keyword} value={self.value}>"

class Var(Stmt):
    def __init__(self, name: Token, initializer: Expr):
        self.name = name
        self.initializer = initializer

    def accept[T](self, visitor: Visitor[T]) -> T:
        return visitor.visit_var_stmt(self)

    def __repr__(self) -> str:
        return f"<Var name={self.name} initializer={self.initializer}>"

class While(Stmt):
    def __init__(self, condition: Expr, body: Stmt):
        self.condition = condition
        self.body = body

    def accept[T](self, visitor: Visitor[T]) -> T:
        return visitor.visit_while_stmt(self)

    def __repr__(self) -> str:
        return f"<While condition={self.condition} body={self.body}>"

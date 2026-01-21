from __future__ import annotations
from abc import ABC, abstractmethod
from typing import Protocol
from zsdtoken import Token

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

class Expr(ABC): 
    @abstractmethod
    def accept[T](self, visitor: Visitor[T]) -> T: ...


class Assign(Expr):
    def __init__(self, name: Token, value: Expr):
        self.name = name
        self.value = value

    def accept[T](self, visitor: Visitor[T]) -> T:
        return visitor.visit_assign_expr(self)

    def __repr__(self) -> str:
        return f"<Assign name={self.name} value={self.value}>"

class Binary(Expr):
    def __init__(self, left: Expr, operator: Token, right: Expr):
        self.left = left
        self.operator = operator
        self.right = right

    def accept[T](self, visitor: Visitor[T]) -> T:
        return visitor.visit_binary_expr(self)

    def __repr__(self) -> str:
        return f"<Binary left={self.left} operator={self.operator} right={self.right}>"

class Call(Expr):
    def __init__(self, callee: Expr, paren: Token, arguments: list[Expr]):
        self.callee = callee
        self.paren = paren
        self.arguments = arguments

    def accept[T](self, visitor: Visitor[T]) -> T:
        return visitor.visit_call_expr(self)

    def __repr__(self) -> str:
        return f"<Call callee={self.callee} paren={self.paren} arguments={self.arguments}>"

class Get(Expr):
    def __init__(self, object: Expr, name: Token):
        self.object = object
        self.name = name

    def accept[T](self, visitor: Visitor[T]) -> T:
        return visitor.visit_get_expr(self)

    def __repr__(self) -> str:
        return f"<Get object={self.object} name={self.name}>"

class Set(Expr):
    def __init__(self, object: Expr, name: Token, value: Expr):
        self.object = object
        self.name = name
        self.value = value

    def accept[T](self, visitor: Visitor[T]) -> T:
        return visitor.visit_set_expr(self)

    def __repr__(self) -> str:
        return f"<Set object={self.object} name={self.name} value={self.value}>"

class Super(Expr):
    def __init__(self, keyword: Token, method: Token):
        self.keyword = keyword
        self.method = method

    def accept[T](self, visitor: Visitor[T]) -> T:
        return visitor.visit_super_expr(self)

    def __repr__(self) -> str:
        return f"<Super keyword={self.keyword} method={self.method}>"

class This(Expr):
    def __init__(self, keyword: Token):
        self.keyword = keyword

    def accept[T](self, visitor: Visitor[T]) -> T:
        return visitor.visit_this_expr(self)

    def __repr__(self) -> str:
        return f"<This keyword={self.keyword}>"

class Grouping(Expr):
    def __init__(self, expression: Expr):
        self.expression = expression

    def accept[T](self, visitor: Visitor[T]) -> T:
        return visitor.visit_grouping_expr(self)

    def __repr__(self) -> str:
        return f"<Grouping expression={self.expression}>"

class Logical(Expr):
    def __init__(self, left: Expr, operator: Token, right: Expr):
        self.left = left
        self.operator = operator
        self.right = right

    def accept[T](self, visitor: Visitor[T]) -> T:
        return visitor.visit_logical_expr(self)

    def __repr__(self) -> str:
        return f"<Logical left={self.left} operator={self.operator} right={self.right}>"

# 'Literal' collides with typing.Literal
class LiteralValue(Expr):
    def __init__(self, value: object):
        self.value = value

    def accept[T](self, visitor: Visitor[T]) -> T:
        return visitor.visit_literalvalue_expr(self)

    def __repr__(self) -> str:
        return f"<LiteralValue value={self.value}>"

class Unary(Expr):
    def __init__(self, operator: Token, right: Expr):
        self.operator = operator
        self.right = right

    def accept[T](self, visitor: Visitor[T]) -> T:
        return visitor.visit_unary_expr(self)

    def __repr__(self) -> str:
        return f"<Unary operator={self.operator} right={self.right}>"

class Variable(Expr):
    def __init__(self, name: Token):
        self.name = name

    def accept[T](self, visitor: Visitor[T]) -> T:
        return visitor.visit_variable_expr(self)

    def __repr__(self) -> str:
        return f"<Variable name={self.name}>"

class Range(Expr):
    def __init__(self, start: int, stop: int, step: int) -> None:
        self.start = start
        self.stop = stop
        self.step = step

    def accept[T](self, visitor: Visitor[T]) -> T:
        return visitor.visit_range_expr(self)
    
    def __repr__(self) -> str:
        return f"<Range start={self.start} stop={self.stop} step={self.step}>"
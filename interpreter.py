from collections.abc import Sequence
from callables import clock, ZSDCallable, ZSDFunction
from environment import Environment
from expr import (
    Assign,
    Binary,
    Call,
    Grouping,
    LiteralValue,
    Logical,
    Unary,
    Variable,
    Visitor as ExprVisitor,
    Expr
)
import stmt
import output
from output import ReturnException, ZSDRuntimeError
from tokentype import TokenType as tt
from zsdtoken import Token
from typing import Any, cast

# region Interpreter
class Interpreter(ExprVisitor[object], stmt.Visitor[None]):
    def __init__(self) -> None:
        self.globals = Environment()
        self.env = self.globals
        self.globals.define("clock", clock)

    def interpret(self, statements: Sequence[stmt.Stmt]):
        try: 
            for statement in statements:
                self.execute(statement)
        except ZSDRuntimeError as e:
            output.runtime_error(e)

    def shadowize(self, object: object):
        if object is None: return "nil"
        return str(object)

    def evaluate(self, expr: Expr):
        return expr.accept(self)
    
    def execute(self, stmt: stmt.Stmt):
        return stmt.accept(self)
    
    def check_type(self, operand: object, operator: Token):
        if isinstance(operand, (float, int)): return
        raise ZSDRuntimeError(operator, "Operand must be a number.")
    
    def check_types(self, operator: Token, left: object, right: object):
        if isinstance(left, (float | int)) and isinstance(right, (float | int)): return
        raise ZSDRuntimeError(operator, "Operands must be numbers.")
    
    def execute_block(self, statements: list[stmt.Stmt], env: Environment):
        previous = self.env
        try:
            self.env = env
            for stmt in statements:
                self.execute(stmt)
        finally: 
            self.env = previous

    def is_truthy(self, value: object):
        # Ruby's implementation
        return value not in (False, None)

    # region visit statements

    def visit_block_stmt(self, stmt: stmt.Block) -> None:
        return self.execute_block(stmt.statements, Environment(self.env))

    def visit_expression_stmt(self, stmt: stmt.Expression) -> None:
        self.evaluate(stmt.expression)
        return
    
    def visit_if_stmt(self, stmt: stmt.If) -> None:
        conditions = iter(stmt.conditions)
        for cond, body in conditions:
            if self.is_truthy(self.evaluate(cond)):
                self.execute(body)
                break
        else:
            if stmt.else_branch:
                self.execute(stmt.else_branch)

    def visit_while_stmt(self, stmt: stmt.While) -> None:
        while self.is_truthy(self.evaluate(stmt.condition)):
            self.execute(stmt.body)
    
    def visit_print_stmt(self, stmt: stmt.Print) -> None:
        value = self.evaluate(stmt.expression)
        return print(value)
    
    def visit_var_stmt(self, stmt: stmt.Var) -> None:
        value = self.evaluate(stmt.initializer)
        self.env.define(stmt.name.lexeme, value)

    def visit_function_stmt(self, stmt: stmt.Function) -> None:
        function = ZSDFunction(stmt, self.env)
        self.env.define(stmt.name.lexeme, function)

    def visit_return_stmt(self, stmt: stmt.Return) -> None:
        raise ReturnException(stmt, self.evaluate(stmt.value))

    # region visit exprs

    def visit_variable_expr(self, expr: Variable) -> object:
        #print(expr.name.lexeme, "for", self.env.get(expr.name))
        return self.env.get(expr.name)
    
    def visit_assign_expr(self, expr: Assign) -> object:
        value = self.evaluate(expr.value)
        self.env.assign(expr.name, value)
        return value

    def visit_literalvalue_expr(self, expr: LiteralValue) -> object:
        return expr.value
    
    def visit_grouping_expr(self, expr: Grouping) -> object:
        return self.evaluate(expr.expression)
    
    def visit_unary_expr(self, expr: Unary) -> object:
        right: Any = self.evaluate(expr.right)

        #if not isinstance(right, (float, int)):
        #    output.error(expr.operator, "Non number")

        match expr.operator.type:
            case tt.MINUS:
                return -right
            case tt.PLUS:
                return abs(right)
            case tt.BANG:
                return not self.is_truthy(right)
            
        raise ValueError
    
    def visit_binary_expr(self, expr: Binary) -> object:
        #print("bin", expr.left, expr.right)
        left: Any = self.evaluate(expr.left)
        right: Any = self.evaluate(expr.right)

        match expr.operator.type:
            case tt.MINUS:
                return left - right
            case tt.STAR:
                return left * right
            case tt.SLASH:
                return left / right
            case tt.PLUS:
                #print("plus", type(left) is type(right))
                if isinstance(left, str) or isinstance(right, str):
                    return str(left) + str(right)
                if isinstance(left, (float, int)) and isinstance(right, (float, int)):
                    return left + right
            case tt.GREATER:
                return left > right
            case tt.GREATER_EQUAL:
                return left >= right
            case tt.LESS:
                return left < right
            case tt.LESS_EQUAL:
                return left <= right
            case tt.EQUAL_EQUAL:
                return left == right
            case tt.BANG_EQUAL:
                return left != right
            
        raise ZSDRuntimeError(expr.operator, "Invalid operand types.")

    def visit_logical_expr(self, expr: Logical) -> object:
        left = self.evaluate(expr.left)

        match expr.operator.type:
            case tt.OR:
                if self.is_truthy(left): 
                    return left
                
            case tt.AND:
                if not self.is_truthy(left): 
                    return left
                
            case _:
                raise ValueError(f"{expr.operator!r}")
            
        return self.evaluate(expr.right)
    
    def visit_call_expr(self, expr: Call) -> object:
        callee = self.evaluate(expr.callee)
        arguments = [self.evaluate(arg) for arg in expr.arguments]

        function = cast(ZSDCallable, callee)
        if (arg_len := len(arguments)) != (arity := function.arity()):
            raise ZSDRuntimeError(
                expr.paren, 
                f"Expected {arity} arguments but received {arg_len} instead."
            )

        return function.call(self, arguments)
from collections.abc import Sequence
import typing
from callables import ZSDCallable, ZSDFunction, ZSDParam
from classes import ZSDClass, ZSDObject, range_class
from environment import Environment
from expr import (
    Assign,
    Binary,
    Call,
    Get,
    Grouping,
    LiteralValue,
    Logical,
    Range,
    Set,
    Super,
    This,
    Unary,
    Variable,
    Visitor as ExprVisitor,
    Expr
)
import stmt
import output
from literals import true, false, nil
from output import ReturnException, ZSDRuntimeError
from tokentype import TokenType as tt
from zsdtoken import Token
from typing import Any, cast

# region Interpreter
class Interpreter(ExprVisitor[object], stmt.Visitor[None]):
    def __init__(self) -> None:
        self.globals = Environment()
        self.env = self.globals
        self.locals: dict[Expr, int] = {}

    def interpret(self, statements: Sequence[stmt.Stmt]):
        try: 
            for statement in statements:
                self.execute(statement)
        except ZSDRuntimeError as e:
            output.runtime_error(e)

    def shadowize(self, object: object):
        if object is None: return nil
        if object is True: return true
        if object is False: return false
        return object

    def evaluate(self, expr: Expr):
        return expr.accept(self)
    
    def execute(self, stmt: stmt.Stmt):
        return stmt.accept(self)
    
    def resolve(self, expr: Expr, depth: int):
        self.locals[expr] = depth
    
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
        return bool(value)

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
        parameters = [ZSDParam(param.name, param.default and self.evaluate(param.default)) for param in stmt.params]
        function = ZSDFunction(stmt, parameters, self.env)
        self.env.define(stmt.name.lexeme, function)

    def visit_return_stmt(self, stmt: stmt.Return):
        raise ReturnException(stmt, self.evaluate(stmt.value))
    
    def visit_class_stmt(self, stmt: stmt.Class) -> None:
        superclass = None
        if stmt.superclass:
            superclass = self.evaluate(stmt.superclass)
            if not isinstance(superclass, ZSDClass):
                raise ZSDRuntimeError(stmt.superclass.name, "Invalid superclass.")

        self.env.define(stmt.name.lexeme, None)

        if stmt.superclass:
            self.env = Environment(self.env)
            self.env.define("super", superclass)

        methods: dict[str, ZSDFunction] = {}
        for method in stmt.methods:
            parameters = [ZSDParam(param.name, param.default and self.evaluate(param.default)) for param in method.params]
            function = ZSDFunction(method, parameters, self.env, method.name.lexeme == "init")
            methods[method.name.lexeme] = function

        klass = ZSDClass(stmt.name.lexeme, methods, superclass)

        if stmt.superclass:
            assert isinstance(self.env.parent_scope, Environment)
            self.env = self.env.parent_scope

        self.env.assign(stmt.name, klass)

    def visit_for_stmt(self, stmt: stmt.For) -> None:
        iterable = self.evaluate(stmt.iterable)
        assert getattr(iterable, "fields", None) is not None
        assert isinstance(iterable, ZSDObject)

        next_func = iterable.klass.find_method("iter")
        if next_func is None:
            raise ZSDRuntimeError(stmt.keyword, f"{iterable.klass.name} object is not iterable.")
        
        iterator = next_func.bind(iterable).call(self, [])
        assert isinstance(iterator, ZSDObject)

        next_func = iterator.klass.find_method("next")
        if next_func is None:
            raise ZSDRuntimeError(stmt.keyword, f"{iterator.klass.name} object is not an iterator.")
        
        self.env.define(stmt.iter_var.lexeme, nil)

        while (next_value := next_func.bind(iterator).call(self, [])) is not nil:
            self.env.assign(stmt.iter_var, next_value)
            self.execute(stmt.body)

    # region visit exprs

    def visit_variable_expr(self, expr: Variable) -> object:
        return self.lookup_variable(expr.name, expr)
    
    def lookup_variable(self, name: Token, expr: Expr):
        distance = self.locals.get(expr, None)
        if distance is not None:
            return self.env.get_at(name.lexeme, distance)
        else:
            return self.globals.get(name)
    
    def visit_assign_expr(self, expr: Assign) -> object:
        value = self.evaluate(expr.value)
        
        distance = self.locals.get(expr, None)
        if distance is not None:
            self.env.assign_at(expr.name.lexeme, value, distance)
        else:
            self.globals.assign(expr.name, value)

        return value

    def visit_literalvalue_expr(self, expr: LiteralValue) -> object:
        return expr.value
    
    def visit_grouping_expr(self, expr: Grouping) -> object:
        return self.evaluate(expr.expression)
    
    def visit_unary_expr(self, expr: Unary) -> object:
        right: Any = self.evaluate(expr.right)

        match expr.operator.type:
            case tt.MINUS:
                return -right
            case tt.PLUS:
                return abs(right)
            case tt.BANG:
                return self.shadowize(not self.is_truthy(right))
            
        raise ValueError
    
    def visit_binary_expr(self, expr: Binary) -> object:
        left: Any = self.evaluate(expr.left)
        right: Any = self.evaluate(expr.right)
        shadowize = self.shadowize

        match expr.operator.type:
            case tt.MINUS | tt.MINUS_EQUAL:
                return shadowize(left - right)
            case tt.STAR | tt.STAR_EQUAL:
                return shadowize(left * right)
            case tt.SLASH | tt.SLASH_EQUAL:
                return shadowize(left / right)
            case tt.PLUS | tt.PLUS_EQUAL:
                if isinstance(left, str) or isinstance(right, str):
                    return str(left) + str(right)
                if isinstance(left, (float, int)) and isinstance(right, (float, int)):
                    return shadowize(left + right)
            case tt.GREATER:
                return shadowize(left > right)
            case tt.GREATER_EQUAL:
                return shadowize(left >= right)
            case tt.LESS:
                return shadowize(left < right)
            case tt.LESS_EQUAL:
                return shadowize(left <= right)
            case tt.EQUAL_EQUAL:
                return shadowize(left == right)
            case tt.BANG_EQUAL:
                return shadowize(left != right)
            
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

        if not isinstance(callee, ZSDCallable):
            assert isinstance(callee, ZSDObject)
            raise ZSDRuntimeError(
                expr.paren,
                f"{callee.klass.name!r} object is not callable."
            )

        function = cast(ZSDCallable, callee)

        arg_len = len(arguments)
        min_arity, max_arity = function.arity()

        s = lambda i: "" if i == 1 else "s"

        if arg_len < min_arity:
            raise ZSDRuntimeError(
                expr.paren, 
                f"Expected at least {min_arity} argument{s(min_arity)} but received {arg_len} instead."
            )
        
        if arg_len > max_arity:
            raise ZSDRuntimeError(
                expr.paren, 
                f"Expected at most {max_arity} argument{s(max_arity)} but received {arg_len} instead."
            )

        return function.call(self, arguments)
    
    def visit_get_expr(self, expr: Get) -> object:
        object = self.evaluate(expr.object)

        if isinstance(object, ZSDObject):
            return object.get(expr.name)
        
        raise ZSDRuntimeError(expr.name, "Invalid attribute accessor.")
        
    def visit_set_expr(self, expr: Set) -> object:
        object = self.evaluate(expr.object)

        if not isinstance(object, ZSDObject):
            raise ZSDRuntimeError(expr.name, "Invalid setter.")
        
        value = self.evaluate(expr.value)
        object.set(expr.name, value)
        return value
    
    def visit_this_expr(self, expr: This) -> object:    
        return self.lookup_variable(expr.keyword, expr)
    
    def visit_super_expr(self, expr: Super) -> object:
        distance = self.locals[expr]
        superclass = typing.cast(ZSDClass, self.env.get_at("super", distance))
        lifesaver = typing.cast(ZSDObject, self.env.get_at("this", distance - 1))

        tboy = superclass.find_method(expr.method.lexeme)
        if tboy is None:
            raise ZSDRuntimeError(expr.method, f"Undefined property {expr.method.lexeme!r}.")

        return tboy.bind(lifesaver)
    
    def visit_range_expr(self, expr: Range) -> object:
        return range_class.call(self, [expr.start, expr.stop, expr.step])
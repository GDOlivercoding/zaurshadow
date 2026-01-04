from enum import Enum, auto
import expr
from expr import Expr
import stmt
from stmt import Stmt
from interpreter import Interpreter
from zsdtoken import Token
import output

class Scope(Enum):
    none = auto()
    function = auto()
    method = auto()
    initializer = auto()

class Class(Enum):
    none = auto()
    klass = auto()

class ScopeEntry:
    def __init__(self, token: Token | None = None, ready=False, used=False) -> None:
        # This attribute points to the variable identifier at declaration
        self.token = token
        self.ready = ready
        self.used = used

class Resolver(expr.Visitor[None], stmt.Visitor[None]):
    def __init__(self, interpreter: Interpreter) -> None:
        self.interpreter = interpreter
        # [{varname: str, meta: {ready: bool, used: bool}}]
        self.scopes: list[dict[str, ScopeEntry]] = []
        self.current_scope: Scope = Scope.none
        self.current_class: Class = Class.none

    # region stmt visits

    def visit_block_stmt(self, stmt: stmt.Block) -> None:
        self.new_scope()
        self.resolve(stmt.statements)
        self.pop_scope()

    def visit_var_stmt(self, stmt: stmt.Var) -> None:
        self.declare(stmt.name)
        if stmt.initializer is not None:
            self.resolve(stmt.initializer)
        self.define(stmt.name)

    def visit_function_stmt(self, stmt: stmt.Function) -> None:
        self.declare(stmt.name)
        self.define(stmt.name)

        self.resolve_function(stmt, Scope.function)

    def visit_expression_stmt(self, stmt: stmt.Expression) -> None:
        self.resolve(stmt.expression)

    def visit_if_stmt(self, stmt: stmt.If) -> None:
        for condition, body in stmt.conditions:
            self.resolve(condition)
            self.resolve(body)

        if stmt.else_branch:
            self.resolve(stmt.else_branch)

    def visit_return_stmt(self, stmt: stmt.Return) -> None:
        if self.current_scope == Scope.none:
            output.error(stmt.keyword, "Return outside function.")

        if stmt.value:
            if self.current_scope == Scope.initializer:
                output.error(stmt.keyword, "Returning a value from an initializer is forbidden.")

            self.resolve(stmt.value)

    def visit_print_stmt(self, stmt: stmt.Print) -> None:
        self.resolve(stmt.expression)

    def visit_while_stmt(self, stmt: stmt.While) -> None:
        self.resolve(stmt.condition)
        self.resolve(stmt.body)

    def visit_class_stmt(self, stmt: stmt.Class) -> None:
        enclosing_class = self.current_class
        self.current_class = Class.klass

        self.declare(stmt.name)
        self.define(stmt.name)

        self.new_scope()
        self.scopes[-1]["this"] = ScopeEntry()

        for method in stmt.methods:
            self.resolve_function(
                method, 
                Scope.initializer if method.name.lexeme == "init" else Scope.method
            )

        self.pop_scope()
        self.current_class = enclosing_class

    # region expr visits

    def visit_variable_expr(self, expr: expr.Variable) -> None:
        if self.scopes and not self.scopes[-1].get(expr.name.lexeme, True):
            output.error(expr.name, "Unbound local variable.")

        self.resolve_local(expr, expr.name)

    def visit_assign_expr(self, expr: expr.Assign) -> None:
        self.resolve(expr.value)
        self.resolve_local(expr, expr.name)

    def visit_binary_expr(self, expr: expr.Binary) -> None:
        self.resolve(expr.left)
        self.resolve(expr.right)

    def visit_unary_expr(self, expr: expr.Unary) -> None:
        self.resolve(expr.right)

    def visit_call_expr(self, expr: expr.Call) -> None:
        self.resolve(expr.callee)

        for arg in expr.arguments:
            self.resolve(arg)

    def visit_grouping_expr(self, expr: expr.Grouping) -> None:
        self.resolve(expr.expression)

    def visit_literalvalue_expr(self, expr: expr.LiteralValue) -> None:
        pass

    def visit_logical_expr(self, expr: expr.Logical) -> None:
        self.resolve(expr.left)
        self.resolve(expr.right)

    def visit_get_expr(self, expr: expr.Get) -> None:
        self.resolve(expr.object)

    def visit_set_expr(self, expr: expr.Set) -> None:
        self.resolve(expr.value)
        self.resolve(expr.object)

    def visit_this_expr(self, expr: expr.This) -> None:
        if self.current_class == Class.none:
            output.error(expr.keyword, "'this' outside class.")

        self.resolve_local(expr, expr.keyword)

    # region utilities

    def resolve(self, item: list[Stmt] | Stmt | Expr):
        if isinstance(item, Expr | Stmt):
            item.accept(self)
        else:
            for stmt in item:
                stmt.accept(self)

    def resolve_local(self, expr: Expr, name: Token):
        # TODO: improve this
        for i, scope in reversed(list(enumerate(self.scopes))):
            if name.lexeme in scope:
                scope[name.lexeme].used = True
                self.interpreter.resolve(expr, len(self.scopes) - 1 - i)
                return
            
    def resolve_function(self, func: stmt.Function, scope_type: Scope):
        enclosing_scope = self.current_scope
        self.current_scope = scope_type
        self.new_scope()

        for param in func.params:
            self.declare(param)
            self.define(param)

        self.resolve(func.body)
        self.pop_scope()
        self.current_scope = enclosing_scope

    def new_scope(self):
        self.scopes.append({})

    def pop_scope(self):
        scope = self.scopes.pop()
        for entry in scope.values():
            if not entry.used and entry.token:
                output.error(entry.token, f"Local variable unused.")

    def declare(self, name: Token):
        if not self.scopes: return
        scope = self.scopes[-1]

        if name.lexeme in scope and (token := scope[name.lexeme].token):
            # TODO: Maybe change this error message in the future lol
            return output.error(token, "Variable redeclaration is forbidden.")

        scope[name.lexeme] = ScopeEntry(name, False)

    def define(self, name: Token):
        if not self.scopes: return  

        scope = self.scopes[-1]
        scope[name.lexeme].ready = True
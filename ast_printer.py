from expr import (
    Visitor, 
    Expr, 
    Binary, 
    Grouping, 
    LiteralValue, 
    Unary
)
from zsdtoken import Token
import tokentype as tt

class ASTPrinter(Visitor[str]):
    def print(self, expr: Expr):
        return expr.accept(self)

    def parenthesize(self, name: str, *exprs: Expr):
        return f"({name}{"".join([" " + expr.accept(self) for expr in exprs])})"
    
    def visit_binary_expr(self, expr: Binary) -> str:
        return self.parenthesize(expr.operator.lexeme, expr.left, expr.right)
    
    def visit_unary_expr(self, expr: Unary) -> str:
        return self.parenthesize(expr.operator.lexeme, expr.right)
    
    def visit_grouping_expr(self, expr: Grouping) -> str:
        return self.parenthesize("group", expr.expression)
    
    def visit_literal_expr(self, expr: LiteralValue) -> str:
        return "nil" if expr.value is None else str(expr.value)
    
def main():
    expression = Binary(
        Unary(
            Token(tt.MINUS, "-", None, 1),
            LiteralValue(123),
        ),
        Token(tt.STAR, "*", None, 1),
        Grouping(LiteralValue(45.67))
    )

    # (* (- 123) (group 45.67))
    print(ASTPrinter().print(expression))

if __name__ == "__main__":
    main()
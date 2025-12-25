from expr import (
    Assign,
    Binary,
    Expr,
    Grouping,
    LiteralValue,
    Unary,
    Variable
)
from output import ParseError
from stmt import Stmt
from zsdtoken import Token

import output
import stmt
import tokentype as tt

class Parser:
    def __init__(self, tokens: list[Token]) -> None:
        self.tokens = tokens
        self.current = 0

    def parse(self) -> list[Stmt]:
        statements: list[Stmt] = []
        while not self.is_at_end():
            # XXX In the book, even if self.declaration() returns
            # None, it gets added to the list
            statement = self.declaration()
            if statement: statements.append(statement)

        return statements
    
    def declaration(self):
        try:
            if self.match(tt.VAR): return self.var_declaration()
            return self.statement()
        except ParseError:
            self.synchronize()
            return 
        
    def var_declaration(self):
        name = self.consume(tt.IDENTIFIER, "Expect variable name.")

        if self.match(tt.EQUAL):
            init = self.expression()
        else: 
            init = LiteralValue(None)

        self.consume(tt.SEMICOLON, "Expect ';' after variable declaration.")
        return stmt.Var(name, init)

    # https://craftinginterpreters.com/statements-and-state.html#assignment-syntax
    def expression(self):
        return self.assignment()

    def equality(self):
        expr: Expr = self.comparison()

        while (self.match(tt.BANG_EQUAL, tt.EQUAL_EQUAL)):
            operator: Token = self.previous()
            right = self.comparison()
            expr = Binary(expr, operator, right)

        if self.match(tt.LEFT_PAREN):
            raise self.error(self.previous(), "Unexpected symbol.")

        return expr

    def statement(self):
        if self.match(tt.PRINT):
            return self.print_statement()
        if self.match(tt.LEFT_BRACE):
            return stmt.Block(self.block())
        
        return self.expr_statement()
    
    def block(self):
        statements: list[Stmt] = []
        while not self.check(tt.RIGHT_BRACE) and not self.is_at_end():
            obj = self.declaration()
            if obj: statements.append(obj)
    
        self.consume(tt.RIGHT_BRACE, "Expect '}' after block.")
        return statements

    def print_statement(self):
        value = self.expression()
        self.consume(tt.SEMICOLON, "Expect ';' after value.")
        return stmt.Print(value)
    
    def expr_statement(self):
        expr = self.expression()
        self.consume(tt.SEMICOLON, "Expect ';' after expression.")
        return stmt.Expression(expr)
    
    def assignment(self):
        expr = self.equality()

        if self.match(tt.EQUAL):
            equals = self.previous()
            value = self.assignment()

            if isinstance(expr, Variable):
                name = expr.name
                return Assign(name, value)
            
            raise self.error(equals, "Invalid assignment target.")
        
        return expr

    def comparison(self):
        expr = self.term()

        while self.match(tt.GREATER, tt.GREATER_EQUAL, tt.LESS, tt.LESS_EQUAL):
            operator = self.previous()
            right = self.term()
            expr = Binary(expr, operator, right)

        return expr
    
    def term(self):
        expr = self.factor()

        while self.match(tt.MINUS, tt.PLUS):
            operator = self.previous()
            right = self.factor()
            expr = Binary(expr, operator, right)

        return expr
    
    def factor(self):
        expr = self.unary()

        while self.match(tt.SLASH, tt.STAR):
            operator = self.previous()
            right = self.unary()
            expr = Binary(expr, operator, right)

        return expr
    
    def unary(self):
        if self.match(tt.PLUS, tt.MINUS, tt.BANG):
            operator = self.previous()
            right = self.unary()
            return Unary(operator, right)
        
        return self.primary()
    
    # the return hint clears up 'Unknown' from being in the return type for some reason
    def primary(self) -> Expr:
        if self.match(tt.TRUE):  return LiteralValue(True)  
        if self.match(tt.FALSE): return LiteralValue(False)
        if self.match(tt.NIL):   return LiteralValue(None)
        
        if self.match(tt.NUMBER, tt.STRING):
            return LiteralValue(self.previous().literal)
        
        if self.match(tt.LEFT_PAREN):
            expr = self.expression()
            self.consume(tt.RIGHT_PAREN, "Expected ')' after expression.")
            return Grouping(expr)
        
        if self.match(tt.IDENTIFIER):
            return Variable(self.previous())
        
        raise self.error(self.peek(), "Expected expression.")

    def match(self, *types: tt.TokenType):
        """Match if the source follows with any of the tokens given"""
        for type in types:
            if self.check(type):
                self.advance()
                return True
            
        return False
    
    def consume(self, type: tt.TokenType, message: str):
        if self.check(type): return self.advance()
        raise self.error(self.peek(), message)
    
    def check(self, type: tt.TokenType):
        if self.is_at_end(): return False
        return self.peek().type == type

    def advance(self):
        if not self.is_at_end(): self.current += 1
        return self.previous()
    
    def is_at_end(self):
        return self.peek().type == tt.EOF
    
    def peek(self):
        return self.tokens[self.current]
    
    def previous(self):
        return self.tokens[self.current - 1]
            
    def error(self, token: Token, message: str):
        output.error(token, message)
        return ParseError()
    
    def synchronize(self):
        self.advance()

        while not self.is_at_end():
            if self.previous().type == tt.SEMICOLON: return

            if self.peek().type in (
                tt.CLASS, tt.DECLARE, tt.VAR, 
                tt.FOR, tt.IF, tt.WHILE, tt.PRINT, 
                tt.RETURN
            ): return

            self.advance()
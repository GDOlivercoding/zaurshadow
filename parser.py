from expr import Binary, Unary, LiteralValue, Expr, Grouping
from zsdtoken import Token
import tokentype as tt
import output

class ParseError(ValueError): pass

class Parser:
    def __init__(self, tokens: list[Token]) -> None:
        self.tokens = tokens
        self.current = 0

    def parse(self):
        try:
            return self.expression()
        except ParseError:
            return None

    def equality(self):
        expr: Expr = self.comparison()

        while (self.match(tt.BANG_EQUAL, tt.EQUAL_EQUAL)):
            operator: Token = self.previous()
            right = self.comparison()
            expr = Binary(expr, operator, right)

        return expr

    expression = equality

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
    
    # the return hint clears up 'Unknown' being in the return type for some reason
    def primary(self) -> LiteralValue | Grouping:
        if self.match(tt.TRUE):  return LiteralValue(True)  
        if self.match(tt.FALSE): return LiteralValue(False)
        if self.match(tt.NIL):   return LiteralValue(None)
        
        if self.match(tt.NUMBER, tt.STRING):
            return LiteralValue(self.previous().literal)
        
        if self.match(tt.LEFT_PAREN):
            expr = self.expression()
            self.consume(tt.RIGHT_PAREN, "Expected ')' after expression.")
            return Grouping(expr)
        
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
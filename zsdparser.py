from expr import (
    Assign,
    Binary,
    Call,
    Expr,
    Get,
    Grouping,
    LiteralValue,
    Logical,
    Set,
    Super,
    This,
    Unary,
    Variable
)
from output import ParseError
from stmt import Param, Stmt
from zsdtoken import Token

import output
import stmt
from literals import false, true, nil
from tokentype import TokenType as tt, TokenType

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

    def equality(self):
        expr: Expr = self.comparison()

        while (self.match(tt.BANG_EQUAL, tt.EQUAL_EQUAL)):
            operator: Token = self.previous()
            right = self.comparison()
            expr = Binary(expr, operator, right)

        return expr

    # region statements

    def statement(self):
        if self.match(tt.IF):  
            return self.if_statement()
        if self.match(tt.PRINT):
            return self.print_statement()
        if self.match(tt.LEFT_BRACE):
            return self.block()
        if self.match(tt.WHILE):
            return self.while_statement()
        if self.match(tt.FOR):
            return self.for_statement()
        if self.match(tt.DECLARE):
            return self.function("function")
        if self.match(tt.RETURN):
            return self.return_statement()
        if self.match(tt.CLASS):
            return self.class_declaration()
        
        return self.expr_statement()
    
    def if_statement(self):
        conditions: list[tuple[Expr, Stmt]] = []

        def consume_condition(name: str):
            condition = self.expression()
            self.consume(tt.LEFT_BRACE, "Expect '{' after %s condition." % name)

            then_branch = self.block()
            conditions.append((condition, then_branch))

        consume_condition("if")

        while self.match(tt.ELSEIF) and not self.is_at_end():
            consume_condition("elseif")

        if self.match(tt.ELSE):
            else_branch = self.statement()
        else: 
            else_branch = None

        return stmt.If(conditions, else_branch)

    # deviation: Here i return a Block instead of the raw statement list
    def block(self):
        """
        Parse a block: A series of statements in a higher scope surrouded by braces.
        This method already assumes the left brace has been consumed
        """
        statements: list[Stmt] = []
        while not self.check(tt.RIGHT_BRACE) and not self.is_at_end():
            obj = self.declaration()
            if obj: statements.append(obj)
    
        self.consume(tt.RIGHT_BRACE, "Expect '}' after block.")
        return stmt.Block(statements)
    
    def while_statement(self):
        condition = self.expression()
        self.consume(tt.LEFT_BRACE, "Expect '{' after expression.")
        body = self.block()

        return stmt.While(condition, body)

    def print_statement(self):
        value = self.expression()
        self.consume(tt.SEMICOLON, "Expect ';' after value.")
        return stmt.Print(value)
    
    def expr_statement(self):
        expr = self.expression()
        self.consume(tt.SEMICOLON, "Expect ';' after expression.")
        return stmt.Expression(expr)
    
    def for_statement(self):
        self.consume(tt.LEFT_PAREN, "Expect '(' after for.")

        if self.match(tt.SEMICOLON):
            initializer = None
        elif self.match(tt.VAR):
            initializer = self.var_declaration()
        else:
            initializer = self.expr_statement()

        if self.check(tt.SEMICOLON):
            condition = LiteralValue(True)
        else:
            condition = self.expression()
        self.consume(tt.SEMICOLON, "Expect ';' after loop condition")

        if self.check(tt.SEMICOLON):
            increment = None
        else:
            increment = self.expression()

        self.consume(tt.RIGHT_PAREN, "Expect ')' after for clauses.")
        self.consume(tt.LEFT_BRACE, "Expect '{' after for loop.")
        body = self.block()

        if increment is not None:
            body = stmt.Block([body, stmt.Expression(increment)])

        body = stmt.While(condition, body)
        if initializer is not None:
            body = stmt.Block([initializer, body])

        return body
    
    def function(self, fn_type: str):
        name = self.consume(tt.IDENTIFIER, f"Expect {fn_type} name.")
        self.consume(tt.LEFT_PAREN, f"Expect '(' after {fn_type} name.")

        had_default = False
        parameters: list[Param] = []

        def param():
            nonlocal had_default

            if len(parameters) > 255:
                self.error(self.peek(), f"Maximum arguments passed to a function exceeded.")

            name = self.consume(tt.IDENTIFIER, "Expect parameter name.")
            if self.match(tt.EQUAL):
                default = self.logical_or()
                had_default = True
            else:
                if had_default:
                    output.error(name, "Cannot follow default parameter with a non default one.")
                default = None

            parameters.append(Param(name, default))
            

        if not self.check(tt.RIGHT_PAREN) and not self.is_at_end():
            param()

        while self.match(tt.COMMA):
            param()

        self.consume(tt.RIGHT_PAREN, f"Expect ')' after parameter field.")
        self.consume(tt.LEFT_BRACE, "Expect '{' after %s declaration" % fn_type)
        body = self.block()
        return stmt.Function(name, parameters, body.statements)
    
    def return_statement(self):
        keyword = self.previous()
        if self.match(tt.SEMICOLON):
            value = LiteralValue(None)
        else:
            value = self.expression()
            self.consume(tt.SEMICOLON, "Expect ';' after expression.")

        return stmt.Return(keyword, value)
    
    def class_declaration(self):
        name = self.consume(tt.IDENTIFIER, "Expect class name.")

        superclass = None
        if self.match(tt.LESS):
            superclass = Variable(self.consume(tt.IDENTIFIER, "Expect superclass name."))

        self.consume(tt.LEFT_BRACE, "Expect '{' after class name.")

        methods: list[stmt.Function] = []
        while not self.check(tt.RIGHT_BRACE) and not self.is_at_end():
            methods.append(self.function("method"))

        self.consume(tt.RIGHT_BRACE, "Expect '}' after class body.")
        return stmt.Class(name, methods, superclass)

    # region sinkhole 

    # lowest precedence is here
    def expression(self):
        return self.assignment()

    def assignment(self):
        expr = self.logical_or()

        if self.match(tt.EQUAL):
            equals = self.previous()
            value = self.logical_or()

            if isinstance(expr, Variable):
                return Assign(expr.name, value)
            elif isinstance(expr, Get):
                return Set(expr.object, expr.name, value)
            
            raise self.error(equals, "Invalid assignment target.")
        
        return expr
    
    def logical_or(self):
        expr = self.logical_and()

        while self.match(tt.OR):
            operator = self.previous()  
            right = self.logical_and()
            expr = Logical(expr, operator, right)

        return expr
    
    def logical_and(self):
        expr = self.equality()

        while self.match(tt.AND):
            operator = self.previous()
            right = self.equality()
            expr = Logical(expr, operator, right)

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
        
        return self.call()
    
    def call(self):
        expr = self.primary()

        while True:
            if self.match(tt.LEFT_PAREN):
                expr = self.finish_call(expr)
            elif self.match(tt.DOT):
                name = self.consume(tt.IDENTIFIER, "Expect identifier after attribute accessor.")
                expr = Get(expr, name)
            else:
                break

        return expr
    
    # the return hint clears up 'Unknown' from being in the return type for some reason
    def primary(self) -> Expr:
        if self.match(tt.TRUE):  return LiteralValue(true)  
        if self.match(tt.FALSE): return LiteralValue(false)
        if self.match(tt.NIL):   return LiteralValue(nil)
        
        # add range
        if self.match(tt.NUMBER, tt.STRING):
            return LiteralValue(self.previous().literal)
        
        if self.match(tt.LEFT_PAREN):
            expr = self.expression()
            self.consume(tt.RIGHT_PAREN, "Expected ')' after expression.")
            return Grouping(expr)
        
        if self.match(tt.THIS):
            return This(self.previous())
        
        if self.match(tt.SUPER):
            keyword = self.previous()
            self.consume(tt.DOT, "Expect attribute access after 'super'.")
            method = self.consume(tt.IDENTIFIER, "Expect identifier after attribute accessor.")
            return Super(keyword, method)
        
        #if self.match(tt.DECLARE):
        #    return self.expression_function()

        if self.match(tt.IDENTIFIER):
            return Variable(self.previous())
        
        raise self.error(self.peek(), "Expected expression.")

    # region parser tools

    def finish_call(self, callee: Expr):
        arguments: list[Expr] = []

        if not self.check(tt.RIGHT_PAREN):
            arguments.append(self.expression())
            while self.match(tt.COMMA):
                arguments.append(self.expression())

        if len(arguments) > 255:
            # This code intentionally reports an error, but it doesn’t throw an error. 
            self.error(self.peek(), "Maximum arity of a function exceeded.")

        # We will use this paren token to report errors later
        paren = self.consume(tt.RIGHT_PAREN, "Expect ')' after arguments.")
        return Call(callee, paren, arguments)
    
    #def expression_function(self):
    #    if self.match(tt.IDENTIFIER):
    #        name = self.previous()
    #    else:
    #        declare = self.previous()
    #        name = Token(tt.IDENTIFIER, "<anonymous>", None, declare.line)
    #
    #    if self.match(tt.LEFT_PAREN):
    #        parameters: list[Token] = []
    #        if not self.check(tt.RIGHT_PAREN):
    #            parameters.append(self.consume(tt.IDENTIFIER, "Expect parameter name."))
    #
    #        while self.match(tt.COMMA):
    #            if len(parameters) > 255:
    #                self.error(self.peek(), f"Maximum arguments passed to a function exceeded.")
    #            parameters.append(self.consume(tt.IDENTIFIER, "Expect parameter name."))
    #
    #        self.consume(tt.RIGHT_PAREN, f"Expect ')' after parameter field ({self.peek()}).")
    #    else:
    #        parameters = []
    #
    #    self.consume(tt.LEFT_BRACE, "Expect '{' after function declaration")
    #    body = self.block()
    #    return stmt.Function(name, parameters, body.statements)

    def match(self, *types: tt):
        """Match if the source follows with any of the tokens given"""
        for type in types:
            if self.check(type):
                self.advance()
                return True
            
        return False
    
    def consume(self, type: TokenType, message: str):
        if self.check(type): return self.advance()
        raise self.error(self.peek(), message)
    
    def check(self, type: TokenType):
        if self.is_at_end(): return False
        return self.peek().type == type

    def advance(self):
        if not self.is_at_end(): self.current += 1
        return self.previous()
    
    def is_at_end(self):
        return self.peek().type == tt.EOF
    
    def peek(self):
        """Retrieve a token at the current index"""
        return self.tokens[self.current]
    
    def previous(self):
        """Retrieve a token before the current index"""
        return self.tokens[self.current - 1]
            
    # region errors

    def error(self, token: Token, message: str):
        """Report an error and return an exception class"""
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
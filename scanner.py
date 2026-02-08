import re
import output
from zsdtoken import Token
from tokentype import TokenType as tt, TokenType, keywords

def intable(s: str):
    try:
        int(s)
    except ValueError:
        return False
    return True

re_varname_valid = re.compile(r"[a-zA-Z\d_]")

# I simply and unfortunately do not know how this works
class Scanner:
    def __init__(self, source: str) -> None:
        self.source = source
        self.tokens: list[Token] = []
        self.start = 0
        self.current = 0
        self.line = 1

    def scan_tokens(self):
        while not self.is_at_end():
            self.start = self.current
            #print(f"scan_tokens(): {self.start=} {self.current=} {self.tokens=}")
            self.scan_token()

        self.tokens.append(Token(tt.EOF, "", None, self.line))
        return self.tokens

    def scan_token(self):
        char = self.advance()
        add_token = self.add_token

        match char:
            case ")": add_token(tt.RIGHT_PAREN)
            case "(": add_token(tt.LEFT_PAREN)
            case "}": add_token(tt.RIGHT_BRACE)
            case "{": add_token(tt.LEFT_BRACE)

            case ",": add_token(tt.COMMA)
            case ".": add_token(tt.DOT) if not intable(self.peek()) else self.parse_number()
            case ";": add_token(tt.SEMICOLON)

            case "-": add_token(tt.MINUS if not self.match("=") else tt.MINUS_EQUAL)
            case "+": add_token(tt.PLUS if not self.match("=") else tt.PLUS_EQUAL)
            case "*": add_token(tt.STAR if not self.match("=") else tt.STAR_EQUAL)

            case "!":
                add_token(tt.BANG_EQUAL if self.match("=") else tt.BANG)
            case ">":
                add_token(tt.GREATER_EQUAL if self.match("=") else tt.GREATER)
            case "<":
                add_token(tt.LESS_EQUAL if self.match("=") else tt.LESS)
            case "=":
                add_token(
                    tt.EQUAL_EQUAL if self.match("=") 
                    else tt.EQUAL_GREATER if self.match(">") 
                    else tt.EQUAL
                )

            case "/":
                if self.match("/"):
                    while self.peek() != "\n" and not self.is_at_end(): 
                        self.advance()

                elif self.match("*"):
                    line = self.line
                    while True:
                        if self.is_at_end():
                            output.errorline(line, "Unterminated multiline comment")
                            break

                        if self.peek() == "*" and self.peek_next() == "/":
                            # consume the trailing boundaries (*/)
                            self.advance()
                            self.advance()
                            break

                        if self.peek() == "\n":
                            self.line += 1

                        self.advance()

                elif self.match("="):
                    add_token(tt.SLASH_EQUAL)

                else:
                    add_token(tt.SLASH)

            case " " | "\r" | "\t": pass
            case "\n": self.line += 1

            case '"': self.parse_string()
        
            case _: 
                if intable(char):
                    self.parse_number()
                elif re_varname_valid.match(char):
                    self.parse_identifier()
                else:
                    output.errorline(self.line, "Unexpected character.")

    def parse_string(self):
        while (
            self.peek() != '"' 
            and not self.is_at_end()
        ):
            if self.peek() == "\n":
                output.errorline(self.line, "Unterminated string at newline.")

            self.advance()

        if self.is_at_end():
            output.errorline(self.line, "Unterminated string at EOF.")

        self.advance()

        value = self.source[self.start+1:self.current-1]
        #print(value)
        self.add_token(tt.STRING, value)

    def parse_number(self):
        while intable(self.peek()): self.advance()
        dot = "." in self.source[self.start:self.current]

        if self.peek() == "." and not dot:
            if intable(self.peek_next()):
                dot = True
                self.advance()
                while intable(self.peek()): self.advance()

            # implement this later
            elif self.peek_next() == ".":
                start = int(self.source[self.start:self.current])
                self.advance()
                self.advance()
                inclusive = self.match("=")

                end_line = self.current
                while intable(self.peek()): self.advance()
                stop = int(self.source[end_line:self.current])
                return self.add_token(tt.RANGE, (start, stop + inclusive))

        init_choice = dot and float or int
        #print(f"parse_float(): {self.start=} {self.current=}")
        self.add_token(tt.NUMBER, init_choice(self.source[self.start:self.current]))

    def parse_identifier(self):
        while re_varname_valid.match(self.peek()): self.advance()

        text = self.source[self.start:self.current]
        type = keywords.get(text, None) or tt.IDENTIFIER
        self.add_token(type)

    def match(self, expected_char: str):
        if self.is_at_end(): return False
        if self.source[self.current] != expected_char: return False

        self.current += 1
        return True

    def peek(self):
        if self.is_at_end(): return "\0"
        return self.source[self.current]
    
    def peek_next(self):
        if self.is_at_end(): return "\0"
        return self.source[self.current+1]

    def advance(self):
        result = self.source[self.current]
        self.current += 1
        return result
    
    def add_token(self, type: TokenType, literal: object = None):
        lexeme = self.source[self.start:self.current]
        self.tokens.append(Token(type, lexeme, literal, self.line))
    
    def is_at_end(self):
        return self.current >= len(self.source)
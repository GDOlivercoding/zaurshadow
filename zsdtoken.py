from tokentype import TokenType
from tokentype import TokenType as tt

class Token:
    def __init__(self, type: TokenType, lexeme: str, literal: object, line: int) -> None:
        self.type = type
        self.lexeme = lexeme
        self.literal = literal
        self.line = line

    def __repr__(self) -> str:
        if self.literal is not None:
            extra = f" literal={self.literal!r}"
        elif self.lexeme:
            extra = f" lexeme={self.lexeme!r}"
        else:
            extra = ""
            
        return f"<ZSDToken {self.type.name} #L{self.line}{extra}>"
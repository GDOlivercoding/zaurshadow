from tokentype import TokenType

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
            
        return f"<Token {self.type.name} L{self.line}{extra}>"
    
    @classmethod
    def frm(
        cls, 
        token: "Token", 
        *, 
        type: TokenType | None = None,
        lexeme: str | None = None, 
        literal: object = None, 
        line: int | None = None
    ):
        noneor = lambda left, right: left if left is not None else right
        return cls(
            noneor(type, token.type), 
            noneor(lexeme, token.lexeme), 
            noneor(literal, token.literal), 
            noneor(line, token.line)
        )

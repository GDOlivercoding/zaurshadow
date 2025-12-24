from typing import TYPE_CHECKING

(
    LEFT_PAREN, RIGHT_PAREN, LEFT_BRACE, RIGHT_BRACE,
    COMMA, DOT, MINUS, PLUS, SEMICOLON, SLASH, STAR,

    BANG, BANG_EQUAL,
    EQUAL, EQUAL_EQUAL,
    GREATER, GREATER_EQUAL,
    LESS, LESS_EQUAL,

    IDENTIFIER, STRING, NUMBER,

    AND, CLASS, ELSE, THIS, FALSE, DECLARE, FOR, IF, NIL, OR,
    PRINT, RETURN, SUPER, TRUE, VAR, WHILE, DO, EOF
    ,*_unused
) = [""] if TYPE_CHECKING else range(100)

for sentinel in (
    var 
    for var in [*globals()] 
    if not var.startswith("_") 
    and isinstance(globals()[var], int)
):
    globals()[sentinel] = sentinel

DOUBLE_QUOTE = '"'
SINGLE_QUOTE = "'"
del _unused

type TokenType = str
from enum import Enum, auto

class TokenType(Enum):
    LEFT_PAREN = auto()
    RIGHT_PAREN = auto()

    LEFT_BRACE = auto()
    RIGHT_BRACE = auto()

    COMMA = auto()
    DOT = auto()
    SEMICOLON = auto()

    MINUS = auto()
    MINUS_EQUAL = auto()
    PLUS = auto()
    PLUS_EQUAL = auto()
    SLASH = auto()
    SLASH_EQUAL = auto()
    STAR = auto()
    STAR_EQUAL = auto()

    BANG = auto()
    BANG_EQUAL = auto()
    EQUAL = auto()
    EQUAL_EQUAL = auto()
    EQUAL_GREATER = auto()
    GREATER = auto()
    GREATER_EQUAL = auto()
    LESS = auto()
    LESS_EQUAL = auto()

    IDENTIFIER = auto()
    STRING = auto()
    NUMBER = auto()
    RANGE = auto()

    PRINT = auto()
    VAR = auto()
    AND = auto()
    OR = auto()
    INSTANCEOF = auto()

    IF = auto()
    ELSEIF = auto()
    ELSE = auto()

    DECLARE = auto()
    RETURN = auto()

    NIL = auto()
    TRUE = auto()
    FALSE = auto()

    CLASS = auto()
    THIS = auto()
    SUPER = auto()

    FOR = auto()
    OF = auto()
    DO = auto()
    WHILE = auto()

    EOF = auto()

keywords: dict[str, TokenType] = {
    "and": TokenType.AND,
    "class": TokenType.CLASS,
    "else": TokenType.ELSE,
    "this": TokenType.THIS,
    "false": TokenType.FALSE,
    "declare": TokenType.DECLARE,
    "for": TokenType.FOR,
    "if": TokenType.IF,
    "elseif": TokenType.ELSEIF,
    "nil": TokenType.NIL,
    "or": TokenType.OR,
    "print": TokenType.PRINT,
    "return": TokenType.RETURN,
    "super": TokenType.SUPER,
    "true": TokenType.TRUE,
    "var": TokenType.VAR,
    "while": TokenType.WHILE,
    "do": TokenType.DO,
    "of": TokenType.OF,
    "instanceof": TokenType.INSTANCEOF
}

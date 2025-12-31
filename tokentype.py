from enum import Enum, auto

class TokenType(Enum):
    LEFT_PAREN = auto()
    RIGHT_PAREN = auto()
    LEFT_BRACE = auto()
    RIGHT_BRACE = auto()
    COMMA = auto()
    DOT = auto()
    MINUS = auto()
    PLUS = auto()
    SEMICOLON = auto()
    SLASH = auto()
    STAR = auto()
    BANG = auto()
    BANG_EQUAL = auto()
    EQUAL = auto()
    EQUAL_EQUAL = auto()
    GREATER = auto()
    GREATER_EQUAL = auto()
    LESS = auto()
    LESS_EQUAL = auto()
    IDENTIFIER = auto()
    STRING = auto()
    NUMBER = auto()
    RANGE = auto()
    EOF = auto()
    AND = auto()
    CLASS = auto()
    ELSE = auto()
    THIS = auto()
    FALSE = auto()
    DECLARE = auto()
    FOR = auto()
    IF = auto()
    ELSEIF = auto()
    NIL = auto()
    OR = auto()
    PRINT = auto()
    RETURN = auto()
    SUPER = auto()
    TRUE = auto()
    VAR = auto()
    WHILE = auto()
    DO = auto()

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
    "do": TokenType.DO
}

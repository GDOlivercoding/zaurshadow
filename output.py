import sys
from typing import TYPE_CHECKING, Final
import stmt
from zsdtoken import Token
from tokentype import TokenType as tt

if TYPE_CHECKING:
    from _typeshed import SupportsWrite

class ZSDRuntimeError(RuntimeError):
    def __init__(self, token: Token, message: str) -> None:
        self.token = token
        self.message = message
        super().__init__(self.message)

class ReturnException(ZSDRuntimeError):
    def __init__(self, return_stmt: stmt.Return, value: object) -> None:
        self.return_stmt = return_stmt
        self.value = value
        self.message = "Return statement outside function."
        super().__init__(self.return_stmt.keyword, self.message)

class ParseError(ValueError): pass

MAX_ARGUMENTS: Final = 255
stream = sys.stdout
had_error = False
had_runtime_error = False

def report(line: int, where: str, message: str):
    global had_error
    had_error = True
    print(f"[Line {line}] Error{where}: {message}", file=stream)

def runtime_error(error: ZSDRuntimeError):
    global had_runtime_error
    had_runtime_error = True
    print(f"[Line {error.token.line}] at {error.token.lexeme!r}: {error.message}", file=stream)


def errorline(line: int, message: str):
    report(line, "", message)

def error(token: Token, message: str):
    if token.type == tt.EOF:
        report(token.line, " at the end", message)
    else:
        report(token.line, f" at {token.lexeme!r}", message)


def reset():
    global had_error, had_runtime_error
    had_error, had_runtime_error = False, False

def set_stream(writable_stream: "SupportsWrite[str]"):
    global stream
    stream = writable_stream
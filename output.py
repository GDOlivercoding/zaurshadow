from zsdtoken import Token
import tokentype as tt

class ZSDRuntimeError(RuntimeError):
    def __init__(self, token: Token, message: str) -> None:
        self.token = token
        self.message = message
        super().__init__(self.message)

class ParseError(ValueError): pass

_had_error = False
_had_runtime_error = False

def report(line: int, where: str, message: str):
    global _had_error
    _had_error = True
    print(f"[Line {line}] Error{where}: {message}")

def errorline(line: int, message: str):
    report(line, "", message)

def error(token: Token, message: str):
    if token.type == tt.EOF:
        report(token.line, " at the end", message)
    else:
        report(token.line, f" at {token.lexeme!r}", message)

def runtime_error(error: ZSDRuntimeError):
    global _had_runtime_error
    _had_runtime_error = True
    print(f"[line {error.token.line}]: {error.message}")

def had_error():
    return _had_error

def had_runtime_error():
    return _had_runtime_error

def reset():
    global _had_error, _had_runtime_error
    _had_error, _had_runtime_error = False, False
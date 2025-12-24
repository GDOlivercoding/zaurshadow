from zsdtoken import Token
import tokentype as tt

_had_error = False

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

def had_error():
    return _had_error
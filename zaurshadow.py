from pathlib import Path
import sys
import time

from callables import ZSDNativeFunction
from scanner import Scanner
from zsdparser import Parser
from resolver import Resolver
from interpreter import Interpreter

import output
from stmt import Expression
from zsdtoken import Token
from tokentype import TokenType as tt
from classes import range_class

clock = ZSDNativeFunction((0, 0), "clock", lambda _, args: time.perf_counter())

def to_string_callback(_, args: list[object]):
    return str(args[0]) if args else ""

to_string = ZSDNativeFunction((0, 1), "str", to_string_callback)

interpreter = Interpreter()
interpreter.env.define("clock", clock)
interpreter.env.define("str", to_string)
interpreter.env.define("range", range_class)

def main():
    if len(sys.argv) > 2:
        raise SystemExit("This file takes a single optional argument.")
    
    elif len(sys.argv) == 1:
        while True:
            line = input("> ")
            runrepl(line)
    
    runfile(Path(sys.argv[1]))

last_token = Token(tt.IDENTIFIER, "_", "", -1)
def runrepl(source: str):
    scanner = Scanner(source)
    tokens = scanner.scan_tokens()

    parser = Parser(tokens)
    statements = parser.parse()

    if output.had_error:
        output.reset()
        return
    
    resolver = Resolver(interpreter)
    resolver.resolve(statements)

    if output.had_error:
        output.reset()
        return
    
    stmt = None
    if len(statements) == 1 and isinstance(stmt := statements[0], Expression):
        try:
            value = interpreter.evaluate(stmt.expression)
        except output.ZSDRuntimeError as e:
            return output.runtime_error(e)
        
        interpreter.env.define(last_token.lexeme, value)
        return print(value)
    
    interpreter.interpret(statements)

    output.reset()

def runfile(file: Path):
    run(file.read_text())

    if output.had_error:
        sys.exit(65)
    if output.had_runtime_error:
        sys.exit(70)

def run(source: str):
    scanner = Scanner(source)
    tokens = scanner.scan_tokens()

    parser = Parser(tokens)
    statements = parser.parse()

    if output.had_error:
        output.reset()
        return
    
    resolver = Resolver(interpreter)
    resolver.resolve(statements)

    if output.had_error:
        output.reset()
        return
    
    interpreter.interpret(statements)

if __name__ == "__main__":
    main()
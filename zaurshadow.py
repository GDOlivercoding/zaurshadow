from pathlib import Path
import sys
from interpreter import Interpreter
from scanner import Scanner
from zsdparser import Parser
import output
from stmt import Expression, Print
from zsdtoken import Token
import tokentype as tt

interpreter = Interpreter()

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
    
    stmt = None
    if len(statements) == 1 and isinstance(stmt := statements[0], Expression):
        value = interpreter.evaluate(stmt.expression)
        interpreter.env.define(last_token, value)
        print(value)
    
    interpreter.interpret(statements)

    #print(interpreter.env)
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
    
    interpreter.interpret(statements)

if __name__ == "__main__":
    main()
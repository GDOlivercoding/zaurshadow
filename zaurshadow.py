from pathlib import Path
import sys
from interpreter import Interpreter
from scanner import Scanner
from parser import Parser
import output

interpreter = Interpreter()

def main():
    if len(sys.argv) > 2:
        raise SystemExit("This file takes a single optional argument.")
    
    elif len(sys.argv) == 1:
        while True:
            line = input("> ")
            run(line)
    
    runfile(Path(sys.argv[1]))

def runfile(file: Path):
    run(file.read_text())

    if output.had_error():
        sys.exit(65)
    if output.had_runtime_error():
        sys.exit(70)

def run(source: str):
    scanner = Scanner(source)
    tokens = scanner.scan_tokens()

    parser = Parser(tokens)
    statements = parser.parse()

    if output.had_error():
        return
    
    interpreter.interpret(statements)
    output.reset()

if __name__ == "__main__":
    main()
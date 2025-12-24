from pathlib import Path
import sys
from scanner import Scanner
from parser import Parser
from ast_printer import ASTPrinter
import output

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
        sys.exit(1)

def run(source: str):
    scanner = Scanner(source)
    tokens = scanner.scan_tokens()
    #print("\n".join([str(s) for s in tokens]))

    parser = Parser(tokens)
    expression = parser.parse()

    if output.had_error() or expression is None:
        return
    
    print(ASTPrinter().print(expression))

if __name__ == "__main__":
    main()
from collections.abc import Callable
from pathlib import Path
import io

# i fucking hate this

def main():
    output_dir = Path(".").parent

    define_ast(output_dir, "Expr", {
        "Assign": [("name", "Token"), ("value", "Expr")],
        "Binary": [("left", "Expr"), ("operator", "Token"), ("right", "Expr")],
        "Grouping": [("expression", "Expr")],
        "Logical": [("left", "Expr"), ("operator", "Token"), ("right", "Expr")],
        "LiteralValue": [("value", "object")],
        "Unary": [("operator", "Token"), ("right", "Expr")],
        "Variable": [("name", "Token")]
    })

    define_ast(output_dir, "Stmt", {
        "Expression": [("expression", "Expr")],
        "If": [("conditions", "list[tuple[Expr, Stmt]]"), ("else_branch", "Stmt | None = None")],
        "Block": [("statements", "list[Stmt]")],
        "Print": [("expression", "Expr")],
        "Var": [("name", "Token"), ("initializer", "Expr")]
    })

def define_ast(output_dir: Path, baseclass: str, types: dict[str, list[tuple[str, str]]]):
    path = output_dir / f"{baseclass.lower()}.py"

    writer = io.StringIO()
    write = lambda s: writer.write(s + "\n")

    write("from __future__ import annotations")
    write("from abc import ABC, abstractmethod")
    write("from typing import Protocol")

    if baseclass == "Stmt":
        write("""from expr import Expr
from zsdtoken import Token""")
    elif baseclass == "Expr":
        write("""from zsdtoken import Token""")

    define_visitor(write, baseclass, types)

    write(f"\nclass {baseclass}(ABC): ")
    write("    @abstractmethod")
    write("    def accept[T](self, visitor: Visitor[T]) -> T: ...\n")

    for classname, fields in types.items():
        define_type(write, baseclass, classname, fields)

    path.write_text(writer.getvalue())

def define_visitor(write: Callable, baseclass: str, types: dict[str, list[tuple[str, str]]]):
    write(f"\nclass Visitor[T](Protocol):")

    for subclass in types.keys():
        write(f"    def visit_{subclass.lower()}_{baseclass.lower()}(self, {baseclass.lower()}: {subclass}) -> T: ...")

def define_type(write: Callable, basename: str, classname: str, field_list: list[tuple[str, str]]):
    if basename == "LiteralValue":
        write("# 'Literal' collides with typing.Literal")

    write(f"\nclass {classname}({basename}):")
    write(f"    def __init__(self{", " + ", ".join([f"{name}: {type}" for name, type in field_list])}):")

    for name, _ in field_list:
        write(f"        self.{name} = {name}")
    write("")
    write(f"    def accept[T](self, visitor: Visitor[T]) -> T:")
    write(f"        return visitor.visit_{classname.lower()}_{basename.lower()}(self)\n")

if __name__ == "__main__":
    main()
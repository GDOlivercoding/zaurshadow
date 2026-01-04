class Nil:
    def __repr__(self) -> str:
        return "nil"

    def __eq__(self, value: object):
        return type(value) is type(self)
    
    def __bool__(self) -> bool:
        return False
    
class TrueClass(int):
    def __init__(self) -> None:
        int.__new__(TrueClass, 1) 

    def __repr__(self) -> str:
        return "true"
    
    def __bool__(self) -> bool:
        return True
    
class FalseClass(int):
    def __init__(self) -> None:
        int.__new__(FalseClass, 0)

    def __repr__(self) -> str:
        return "false"
    
    def __bool__(self) -> bool:
        return False
    
false = FalseClass()
true = TrueClass()
nil = Nil()
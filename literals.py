class NilType:
    def __repr__(self) -> str:
        return "nil"

    def __eq__(self, value: object):
        return type(value) is type(self)
    
    def __bool__(self) -> bool:
        return False
    
class TrueType(int):
    def __init__(self) -> None:
        int.__new__(TrueType, 1) 

    def __repr__(self) -> str:
        return "true"
    
    def __bool__(self) -> bool:
        return True
    
class FalseType(int):
    def __init__(self) -> None:
        int.__new__(FalseType, 0)

    def __repr__(self) -> str:
        return "false"
    
    def __bool__(self) -> bool:
        return False
    
class StopIterationType:
    def __repr__(self) -> str:
        return "StopIteration"

ZSDStopIteration = StopIterationType()
false = FalseType()
true = TrueType()
nil = NilType()
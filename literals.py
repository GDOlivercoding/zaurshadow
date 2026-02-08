class NilType:
    def __repr__(self) -> str:
        return "nil"

    def __eq__(self, value: object):
        return type(value) is type(self)
    
    def __bool__(self) -> bool:
        return False
    
class TrueType(int):
    def __new__(cls):
        return int.__new__(cls, 1)

    def __repr__(self) -> str:
        return "true"
    
    def __bool__(self) -> bool:
        return True
    
class FalseType(int):
    def __new__(cls):
        return int.__new__(cls, 0)

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
def decorator(callable):
    def wrapper(self, *args, **kwargs):
        self.number = 6
        return callable(self, *args, **kwargs)
    return wrapper

class Class:
    def __init__(self) -> None:
        self.number = 5
        setattr(self, "method", decorator(self.method))

    def method(self):
        return self.number
    
inst = Class()
print(inst.method())
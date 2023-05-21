from abc import ABC, abstractmethod

class AbstractClassExample(ABC):
    @abstractmethod
    def do_something(self):
        pass

class AnotherSubclass(AbstractClassExample):
    def another_method(self):
        super().do_something()
        print("The subclass is ", self)

x = AnotherSubclass()

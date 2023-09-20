from abc import ABC, abstractmethod

class Model(ABC):
    @abstractmethod
    def get_id(self) -> int:
        pass

    def get_name(self) -> str:
        return self.__class__.__name__

    @abstractmethod
    def predict(self, prompt: str, input_data: str) -> str:
        pass

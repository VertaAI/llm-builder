from .abc import Model
from testing import generate_string


class Nop(Model):
    def __init__(self, id: int):
        self._id = id

    def get_id(self) -> int:
        return self._id

    def predict(self, prompt: str, input_data: str) -> str:
        return generate_string(1, 5)

from dataclasses import dataclass

@dataclass
class Prompt:
    id: int
    name: str
    prompt: str

    def __init__(self, id: int, name: str, prompt: str):
        self.id = id
        self.name = name
        self.prompt = prompt

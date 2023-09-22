from dataclasses import dataclass
from dataclasses_json import dataclass_json
import json
import dataclasses
import os

@dataclass_json
@dataclass
class Prompt:
    id: int
    prompt: str

    def __init__(self, id: int, prompt: str):
        self.id = id
        self.prompt = prompt

    def save(self):
        directory = "../data/prompts"
        os.makedirs(directory, exist_ok=True)
        with open(os.path.join(directory, "{}.json".format(self.id)), "w") as f:
            json.dump(dataclasses.asdict(self), f, indent=4)

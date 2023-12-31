import dataclasses
import json
import os
from dataclasses import dataclass

from dataclasses_json import dataclass_json


@dataclass_json
@dataclass
class Prompt:
    id: int
    name: str
    description: str
    prompt: str

    def __init__(self, id: int, name: str, description: str, prompt: str):
        self.id = id
        self.name = name
        self.description = description
        self.prompt = prompt

    def get_name(self):
        return self.name

    def save(self):
        directory = "../data/prompts"
        os.makedirs(directory, exist_ok=True)
        with open(os.path.join(directory, "{}.json".format(self.id)), "w") as f:
            json.dump(dataclasses.asdict(self), f, indent=4)

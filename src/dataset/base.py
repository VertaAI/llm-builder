from dataclasses import dataclass
from dataclasses_json import dataclass_json
from typing import List

@dataclass_json
@dataclass
class Sample:
    id: int
    input_data: str
    output_data: str

    def __init__(self, id: int, input_data: str, output_data: str):
        self.id = id
        self.input_data = input_data
        self.output_data = output_data

@dataclass_json
@dataclass
class Dataset:
    id: int
    name: str
    samples: List[Sample]

    def __init__(self, id: int, name: str, samples: List[Sample]):
        self.id = id
        self.name = name
        self.samples = samples

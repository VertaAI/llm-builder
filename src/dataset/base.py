import dataclasses
import json
import os
from dataclasses import dataclass
from typing import List

from dataclasses_json import dataclass_json


@dataclass_json
@dataclass
class Record:
    id: int
    input_data: str
    ground_truth: str
    type: str
    metadata: str

    def __init__(self, id: int, input_data: str, ground_truth: str, type: str = "text", metadata: str = "{}"):
        self.id = id
        self.input_data = input_data
        self.ground_truth = ground_truth
        self.type = type
        self.metadata = metadata


@dataclass_json
@dataclass
class Dataset:
    id: int
    name: str
    records: List[Record]

    def __init__(self, id: int, name: str, records: List[Record]):
        self.id = id
        self.name = name
        self.records = records

    def save(self):
        directory = "../data/datasets"
        os.makedirs(directory, exist_ok=True)
        with open(os.path.join(directory, "{}.json".format(self.id)), "w") as f:
            json.dump(dataclasses.asdict(self), f, indent=4)

    def update_record(self, record):
        for s in self.records:
            if s.id == record.id:
                s.input_data = record.input_data
                s.ground_truth = record.ground_truth
                break
        self.save()

    def add_record(self, record_content: str, ground_truth: str = ""):
        record = Record(len(self.records), record_content, ground_truth)
        self.records.append(record)
        self.save()
        return record

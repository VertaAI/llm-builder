import random
from typing import List
from prompts.base import Prompt
import os
from dataset.base import Dataset, Sample
import pandas as pd
import dataclasses
import json

# List of sample words
sample_words = [
    "Lorem", "ipsum", "dolor", "sit", "amet", "consectetur", "adipiscing", "elit",
    "sed", "do", "eiusmod", "tempor", "incididunt", "ut", "labore", "et", "dolore",
    "magna", "aliqua", "Ut", "enim", "ad", "minim", "veniam", "quis", "nostrud",
    "exercitation", "ullamco", "laboris", "nisi", "ut", "aliquip", "ex", "ea", "commodo",
    "consequat", "Duis", "aute", "irure", "dolor", "in", "reprehenderit", "in", "voluptate",
    "velit", "esse", "cillum", "dolore", "eu", "fugiat", "nulla", "pariatur", "Excepteur", "sint",
    "occaecat", "cupidatat", "non", "proident", "sunt", "in", "culpa", "qui", "officia",
    "deserunt", "mollit", "anim", "id", "est", "laborum"
]

# Function to generate a random "Lorem Ipsum"-like sentence
def generate_string(min_words=5, max_words=10):
    num_words = random.randint(min_words, max_words)
    sentence = ' '.join(random.choice(sample_words) for _ in range(num_words))
    return sentence


def generate_data():
    datasets: List[Dataset] = [
        Dataset(i, generate_string(1,1), [
            Sample(j, generate_string(1,3), generate_string(1,3))
            for j in range(5)
        ])
        for i in range(2)
    ]

    prompts: List[Prompt] = [
        Prompt(i, generate_string(1,1), generate_string(1,3))
        for i in range(2)
    ]

    # Clear the datasets folder
    for filename in os.listdir("../data/datasets"):
        os.remove("../data/datasets/{}".format(filename))
    # Clear the prompts folder
    for filename in os.listdir("../data/prompts"):
        os.remove("../data/prompts/{}".format(filename))

    # Save the datasets to yaml files
    for dataset in datasets:
        with open("../data/datasets/{}.json".format(dataset.name), "w") as f:
            json.dump(dataclasses.asdict(dataset), f, indent=4)

    # Save the prompts to yaml files
    for prompt in prompts:
        with open("../data/prompts/{}.json".format(prompt.name), "w") as f:
            json.dump(dataclasses.asdict(prompt), f, indent=4)

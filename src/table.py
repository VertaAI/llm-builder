from prompts.base import Prompt
import os
from dataset.base import Dataset
import json

def load_data():
    # Load datasets from yaml files
    datasets = []
    # Loop over all the files in the dataset folder
    for filename in os.listdir("../data/datasets"):
        # Open the file
        with open("../data/datasets/{}".format(filename), "r") as f:
            # Load the dataset from the file
            dataset = json.load(f)
            dataset = Dataset.from_dict(dataset)
            # Add the dataset to the list of datasets
            datasets.append(dataset)

    # Load prompts from yaml files
    prompts = []
    # Loop over all the files in the prompt folder
    for filename in os.listdir("../data/prompts"):
        # Open the file
        with open("../data/prompts/{}".format(filename), "r") as f:
            # Load the prompt from the file
            prompt = json.load(f)
            prompt = Prompt.from_dict(prompt)
            # Add the prompt to the list of prompts
            prompts.append(prompt)

    return (datasets, prompts)

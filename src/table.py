from prompts.base import Prompt
import os
from dataset.base import Dataset
import json
import itertools
from computation import load_or_compute
import pandas as pd

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

def create_table(datasets, models, prompts, cached=True):
    data = {
        'model': [],
        'prompt name': [],
        'prompt content': [],
        'dataset': [],
        'sample id': [],
        'sample input': [],
        'sample output': [],
        'prediction': [],
    }

    for dataset in datasets:
        for (model, prompt, sample) in itertools.product(models, prompts, dataset.samples):
            if cached:
                prediction = load_or_compute(model, prompt, dataset, sample)
            else:
                prediction = model.predict(prompt, sample.input_data)
            data['model'].append(model.get_name())
            data['prompt name'].append(prompt.name)
            data['prompt content'].append(prompt.prompt)
            data['dataset'].append(dataset.name)
            data['sample id'].append(sample.id)
            data['sample input'].append(sample.input_data)
            data['sample output'].append(sample.output_data)
            data['prediction'].append(prediction)

    df = pd.DataFrame(data)

    return df

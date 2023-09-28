import itertools
import json
import os

import pandas as pd

from dataset.base import Dataset
from prompts.base import Prompt


def load_config():
    return json.load(open("../data/app_config.json"))


def load_datasets():
    # Load datasets from yaml files
    datasets = []
    # Loop over all the files in the dataset folder
    if os.path.exists("../data/datasets"):
        for filename in os.listdir("../data/datasets"):
            # Open the file
            with open("../data/datasets/{}".format(filename), "r") as f:
                # Load the dataset from the file
                dataset = json.load(f)
                dataset = Dataset.from_dict(dataset)
                # Add the dataset to the list of datasets
                datasets.append(dataset)
    return datasets


def load_data():
    # Load datasets from yaml files
    datasets = []
    # Loop over all the files in the dataset folder
    if os.path.exists("../data/datasets"):
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
    if os.path.exists("../data/prompts"):
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
        'prompt': [],
        'dataset': [],
        'id': [],
        'input': [],
        'groundtruth': [],
        'output': [],
    }

    for dataset in datasets:
        for (model, prompt, record) in itertools.product(models, prompts, dataset.records):
            prediction = model.predict(prompt, record.input_data)
            data['model'].append(model.get_name())
            data['prompt'].append(prompt.prompt)
            data['dataset'].append(dataset.name)
            data['id'].append(record.id)
            data['input'].append(record.input_data)
            data['groundtruth'].append(record.ground_truth)
            data['output'].append(prediction)

    df = pd.DataFrame(data)

    return df


def create_empty_table():
    data = {
        'model': ['davinci', 'davinci'],
        'prompt content': ['lawyer', 'harrypotter'],
        'dataset': ['sample1', 'sample2'],
        'record id': ['1', '1'],
        'input': ['gen ai genai', 'gen ai genai2'],
        'groundtruth': ['', ''],
        'output': ['genai', 'genai2'],
        'timestamp': ['000', '001']
    }

    df = pd.DataFrame(data)

    return df


def read_results():
    from pathlib import Path
    path = str(Path(os.path.abspath(__file__)).parent.parent.as_posix()) + "/cache/"
    import glob

    data = {
        'timestamp': [],
        'input': [],
        'output': [],
        'model': [],
        'prompt': [],
        'dataset': [],
        'id': [],
        'groundtruth': [],
    }

    # root_dir needs a trailing slash (i.e. /root/dir/)
    for filename in glob.iglob(path + '*/*/*/*.txt', recursive=True):
        model_snippet, prompt_snippet, dataset_snippet, record_snippet = filename.split(path)[1].split("/")
        model_name = model_snippet.split("_")[1]
        prompt_id = prompt_snippet.split("_")[1]
        dataset_id = dataset_snippet.split("_")[1]
        record_id = record_snippet.split(".txt")[0].split("_")[1]
        timestamp = record_snippet.split(".txt")[0].split("_")[2]

        prediction = ""
        with open(filename, "r") as f:
            prediction = f.read().strip()

        # read record
        dataset = None
        with open("../data/datasets/{}.json".format(dataset_id), "r") as f:
            # Load the dataset from the file
            dataset = json.load(f)
            dataset = Dataset.from_dict(dataset)

        filtered_records = filter(lambda rec: str(rec.id) == str(record_id), dataset.records)
        record = next(filtered_records, None)
        if record is not None:
            data['model'].append(model_name)
            data['prompt'].append(prompt_id)
            data['dataset'].append(dataset_id)
            data['id'].append(record_id)
            data['input'].append(record.input_data)
            data['groundtruth'].append(record.ground_truth)
            data['output'].append(prediction)
            data['timestamp'].append(timestamp)

    df = pd.DataFrame(data)
    df.sort_values(by='timestamp', ascending=False, inplace=True)

    return df

from models.abc import Model
from typing import List
from models.nop import Nop
import streamlit as st
from prompts.base import Prompt
import os
from dataset.base import Dataset, Sample
import pandas as pd
import dataclasses
import json
import itertools
from testing import generate_string

models: List[Model] = [
    Nop(0),
]

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

# generate_data()
(datasets, prompts) = load_data()

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
        data['model'].append(model.get_name())
        data['prompt name'].append(prompt.name)
        data['prompt content'].append(prompt.prompt)
        data['dataset'].append(dataset.name)
        data['sample id'].append(sample.id)
        data['sample input'].append(sample.input_data)
        data['sample output'].append(sample.output_data)
        data['prediction'].append(model.predict(prompt, sample.input_data))


# Create a DataFrame from the sample data
df = pd.DataFrame(data)

# Create a Streamlit app
st.title('Streamlit Table Example')
st.write('This is a simple table created using Streamlit.')

# Display the table using st.table()
st.table(df)

from models.abc import Model
from typing import List
from models.nop import Nop
import streamlit as st
from prompts.base import Prompt
from dataset.base import Dataset, Sample
import pandas as pd
import itertools
from testing import generate_string

models: List[Model] = [
    Nop(0),
]

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

data = {
    'model': [],
    'dataset': [],
    'sample': [],
    'prompt': [],
}

for dataset in datasets:
    for (sample, model, prompt) in itertools.product(dataset.samples, models, prompts):
        data['model'].append(model.get_name())
        data['dataset'].append(dataset.name)
        data['sample'].append(sample.id)
        data['prompt'].append(prompt.name)

# Create a DataFrame from the sample data
df = pd.DataFrame(data)

# Create a Streamlit app
st.title('Streamlit Table Example')
st.write('This is a simple table created using Streamlit.')

# Display the table using st.table()
st.table(df)

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
from testing import generate_data
from table import load_data, create_table
from computation import run_all_computations, load_or_compute, run_computations

models: List[Model] = [
    Nop(0),
]

# generate_data()
(datasets, prompts) = load_data()

# Create a DataFrame from the sample data
st.title('LLM builder')

st.subheader('Prompt playground')

model_options = [model.get_name() for model in models]
model_selection = st.selectbox('Select a model:', model_options)

dataset_options = [dataset.name for dataset in datasets]
dataset_selection = st.selectbox('Select a dataset:', dataset_options)

prompt_name = st.text_input("Enter a prompt name:")
promp_content = st.text_area("Enter a testing prompt:", height=200)

try_button = st.button("Try prompt")
save_button = st.button("Save prompt")

if try_button:
    model = [m for m in models if m.get_name() == model_selection][0]
    dataset = [d for d in datasets if d.name == dataset_selection][0]
    st.table(create_table([dataset], [model], [Prompt('', prompt_name, promp_content)], cached=False))

if save_button:
    model = [m for m in models if m.get_name() == model_selection][0]
    dataset = [d for d in datasets if d.name == dataset_selection][0]
    prompt_id = len(prompts)
    prompt = Prompt(prompt_id, prompt_name, promp_content)
    prompt.save()
    run_computations(model, prompt, dataset)
    (datasets, prompts) = load_data()
    # TODO: clear table and rest of playground

st.subheader('Data collected so far')

st.table(create_table(datasets, models, prompts, cached=True))

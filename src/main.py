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

st.subheader('Dataset import')
st.write("TODO: some explanation of format")
uploaded_dataset = st.file_uploader("Dataset to import:", type=["csv", "json"])
if uploaded_dataset is not None:
    bytes_data = uploaded_dataset.getvalue()
    dataset_dict = json.loads(bytes_data)
    st.json(dataset_dict)

    dataset_name = st.text_input("Enter a dataset name:") # TODO: make required
    if st.button("Import"):
        dataset_id = len(datasets)
        dataset_dict['id'] = dataset_id
        dataset_dict['name'] = dataset_name
        dataset = Dataset.from_dict(dataset_dict)
        dataset.save()
        (datasets, prompts) = load_data()

st.subheader('Prompt playground')
model_options = [model.get_name() for model in models]
model_selection = st.selectbox('Select a model:', model_options)

dataset_options = [dataset.name for dataset in datasets]
dataset_selection = st.selectbox('Select a dataset:', dataset_options)

prompt_name = st.text_input("Enter a prompt name:") # TODO: make required
promp_content = st.text_area("Enter a testing prompt:", height=200) # TODO: make required

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

st.subheader('LLM Library')

# st.table(create_table(datasets, models, prompts, cached=True))

df = create_table(datasets, models, prompts, cached=True)
df_with_selections = df.copy()
df_with_selections.insert(0, "Select", False)
edited_df = st.data_editor(
    df_with_selections,
    hide_index=True,
    column_config={"Select": st.column_config.CheckboxColumn(required=True)},
    disabled=df.columns,
)
# TODO: can we set the width of the table to be bigger?
selected_rows = edited_df[edited_df.Select]
selection = selected_rows.drop('Select', axis=1)
st.write("Selected rows:")
st.write(selection)
# TODO: hide index on the table above

@st.cache_data
def convert_df(df):
   return df.to_csv(index=False).encode('utf-8')

# TODO: revisit the way that we are downloading. Remove columns? Save to json?
csv = convert_df(selection)

st.download_button(
   "Export selection",
   csv,
   "dataset.csv",
   "text/csv",
   key='download-csv'
)

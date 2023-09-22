import time

import streamlit as st
import table
import json
from dataset.base import Dataset
from dataset.base import Sample
import pandas as pd
from st_aggrid import AgGrid, ColumnsAutoSizeMode, GridOptionsBuilder, GridUpdateMode, DataReturnMode

(datasets, prompts) = table.load_data()

st.subheader('Dataset Management')

selected_dataset_name = st.selectbox('Select a dataset to work with:', [d.name for d in datasets])
with st.form('create_ds', clear_on_submit=True):
    create_ds_name = st.text_input("Or create a new dataset:", placeholder='Enter a dataset name')
    if st.form_submit_button('Create'):
        Dataset(len(datasets), name=create_ds_name, samples=[]).save()
        st.info('Dataset created!')
        st.experimental_rerun()


selected_dataset = filter(lambda d: d.name == selected_dataset_name, datasets).__next__()

samples_frame = pd.DataFrame(selected_dataset.samples, columns=['id', 'input_data', 'output_data'])
st.subheader('Dataset samples')

gb = GridOptionsBuilder.from_dataframe(samples_frame)
gb.configure_default_column(groupable=True, value=True, enableRowGroup=True, autoHeight=True)
gb.configure_selection(selection_mode="single", use_checkbox=False)
samples_grid = AgGrid(
    samples_frame,
    data_return_mode=DataReturnMode.AS_INPUT,
    update_mode=GridUpdateMode.SELECTION_CHANGED,
    columns_auto_size_mode=ColumnsAutoSizeMode.NO_AUTOSIZE,
    gridOptions=gb.build())

selected = samples_grid["selected_rows"]

sample = None
if len(selected) == 1:
    st.subheader('Update sample')
    sample = [s for s in selected_dataset.samples if s.id == selected[0]['id']][0]
    ds_input = sample.input_data
    ds_output = sample.output_data
    sample_id = sample.id
else:
    st.subheader('Create new sample')
    ds_input = ''
    ds_output = ''
    sample_id = len(selected_dataset.samples)

with st.form("add a sample", clear_on_submit=True):
    dataset_input = st.text_area("Document to summarize:", height=300, value=ds_input)
    dataset_output = st.text_area("Expected summary (optional):", height=200, value=ds_output)
    prompt = "Create" if sample is None else "Update"
    if st.form_submit_button(prompt):
        if dataset_input == '':
            st.error('Document cannot be empty')
        else:
            if sample:
                sample.input_data = dataset_input
                sample.output_data = dataset_output
                selected_dataset.update_sample(sample)
            else:
                selected_dataset.samples.append(Sample(len(selected_dataset.samples), dataset_input, dataset_output))
                selected_dataset.save()
            st.info('Sample saved to the Library!')
            (datasets, prompts) = table.load_data()
            st.experimental_rerun()

# Import code below

st.subheader('Dataset import')
st.write("TODO: some explanation of format")
uploaded_dataset = st.file_uploader("Dataset to import:", type=["csv", "json"])
if uploaded_dataset is not None:
    bytes_data = uploaded_dataset.getvalue()
    dataset_dict = json.loads(bytes_data)
    st.json(dataset_dict)

    dataset_name = st.text_input("Enter a dataset name:")
    if st.button("Import"):
        if dataset_name == '':
            st.error('Dataset name cannot be empty')
        else:
            dataset_id = len(datasets)
            dataset_dict['id'] = dataset_id
            dataset_dict['name'] = dataset_name
            dataset = Dataset.from_dict(dataset_dict)
            dataset.save()

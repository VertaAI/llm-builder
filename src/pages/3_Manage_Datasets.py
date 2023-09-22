import time

import streamlit as st
import table
import json
from dataset.base import Dataset
from dataset.base import Sample
import pandas as pd
from st_aggrid import AgGrid, ColumnsAutoSizeMode, GridOptionsBuilder, GridUpdateMode, DataReturnMode

(datasets, prompts) = table.load_data()


def create_table(ds):

    data = {
        'name': [],
        'input doc': [],
        'expected summary': [],
    }

    for d in ds:
        for sample in d.samples:
            data['name'].append(d.name)
            data['input doc'].append(sample.input_data[:200])
            if len(sample.input_data) > 200:
                data['input doc'][-1] += '...'
            data['expected summary'].append(sample.output_data)
            # print("summ: " + data['expected summary'][-1])
    return pd.DataFrame(data)


st.subheader('Existing Datasets')
# st.info('creating table...' + str(time.time_ns()))
df = create_table(datasets)
gb = GridOptionsBuilder.from_dataframe(df)
gb.configure_default_column(groupable=True, value=True, enableRowGroup=True, wrapText=True, autoHeight=True)
gb.configure_selection(selection_mode="single", use_checkbox=False)
existing = AgGrid(
    df,
    data_return_mode=DataReturnMode.FILTERED,
    update_mode=GridUpdateMode.SELECTION_CHANGED,
    height=300,
    columns_auto_size_mode=ColumnsAutoSizeMode.FIT_CONTENTS,
    gridOptions=gb.build(),
    key='grid')

selected = existing["selected_rows"]

if len(selected) == 1:
    st.subheader('Update dataset')
    dataset = [d for d in datasets if d.name == selected[0]['name']][0]
    ds_name = dataset.name
    ds_input = dataset.samples[0].input_data
    ds_output = dataset.samples[0].output_data
    dataset_id = dataset.id
else:
    st.subheader('Create new dataset')
    ds_name = ''
    ds_input = ''
    ds_output = ''
    dataset_id = len(datasets)


with st.form("new_dataset"):
    dataset_name = st.text_input("Enter a dataset name:", value=ds_name)
    dataset_input = st.text_area("Document to summarize:", height=300, value=ds_input)
    dataset_output = st.text_area("Expected summary (optional):", height=200, value=ds_output)
    prompt = "Update" if len(selected) == 1 else "Create"
    if st.form_submit_button(prompt):
        if dataset_name == '' or dataset_input == '':
            st.error('Dataset name and document cannot be empty')
        else:
            dataset_dict = {
                'id': dataset_id,
                'name': dataset_name,
                'samples': [Sample(0, dataset_input, dataset_output)]
            }
            dataset = Dataset.from_dict(dataset_dict)
            dataset.save()
            st.info('Dataset saved to the Library!')
            (datasets, prompts) = table.load_data()


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

import time

import streamlit as st
import table
import json
from dataset.base import Dataset
from dataset.base import Record
import pandas as pd
from st_aggrid import AgGrid, ColumnsAutoSizeMode, GridOptionsBuilder, GridUpdateMode, DataReturnMode

st.set_page_config(page_title='Dataset Library', layout="wide")

(datasets, prompts) = table.load_data()

st.subheader('Current Datasets')
dataset_names = [d.name for d in datasets]
working_name = st.session_state.pop("dataset_name", None)
ds_idx = 0
if working_name is not None:
    ds_idx = dataset_names.index(working_name)

selected_dataset_name = st.selectbox('Select a dataset to work with:', dataset_names, index=ds_idx)
# with st.form('create_ds', clear_on_submit=True):
#     create_ds_name = st.text_input("Or create a new dataset:", placeholder='Enter a dataset name')
#     if st.form_submit_button('Create'):
#         Dataset(len(datasets), name=create_ds_name, records=[]).save()
#         st.info('Dataset created!')
#         # select the newly created dataset and rerun
#         st.session_state['dataset_name'] = create_ds_name
#         st.experimental_rerun()


selected_dataset = filter(lambda d: d.name == selected_dataset_name, datasets).__next__()

records_frame = pd.DataFrame(selected_dataset.records, columns=['id', 'type', 'input_data', 'ground_truth'])
st.subheader('Dataset records')

gb = GridOptionsBuilder.from_dataframe(records_frame)
gb.configure_default_column(groupable=True, value=True, enableRowGroup=True, autoHeight=True)
gb.configure_selection(selection_mode="single", use_checkbox=False)
gb.configure_column("id", hide=True)
records_grid = AgGrid(
    records_frame,
    data_return_mode=DataReturnMode.AS_INPUT,
    update_mode=GridUpdateMode.SELECTION_CHANGED,
    columns_auto_size_mode=ColumnsAutoSizeMode.FIT_ALL_COLUMNS_TO_VIEW,
    gridOptions=gb.build())

with st.expander('Edit Current Dataset'):
    selected = records_grid["selected_rows"]

    record = None
    if len(selected) == 1:
        st.subheader('Update record')
        record = [s for s in selected_dataset.records if s.id == selected[0]['id']][0]
        ds_input = record.input_data
        ds_output = record.ground_truth
    else:
        st.subheader('Create new records')
        ds_input = ''
        ds_output = ''

    with st.form("add a record", clear_on_submit=True):
        dataset_input = st.text_area("Document to summarize:", height=300, value=ds_input)
        dataset_output = st.text_area("Ground truth summary (optional):", height=200, value=ds_output)
        prompt = "Create" if record is None else "Update"
        if st.form_submit_button(prompt):
            if dataset_input == '':
                st.error('Document cannot be empty')
            else:
                if record:
                    record.input_data = dataset_input
                    record.ground_truth = dataset_output
                    selected_dataset.update_record(record)
                else:
                    selected_dataset.records.append(Record(len(selected_dataset.records), dataset_input, dataset_output))
                    selected_dataset.save()
                st.info('Record saved to the Library!')
                (datasets, prompts) = table.load_data()
                st.experimental_rerun()

# Import code below

with st.expander('New Dataset Import'):
    st.write("Create a new dataset by listing the summarization URLs. Include 1 URL per line")

    urls = st.text_area("URLs")
    create_ds_name = st.text_input("Dataset Name:", placeholder='Enter a dataset name')

    if st.button("Create Dataset"):
        dataset_id = len(datasets)
        dataset_dict = {}
        dataset_dict['id'] = dataset_id
        dataset_dict['name'] = create_ds_name
        
        records = []
        for idx, url in enumerate(urls.split("\n")):
            records.append(Record(
                id=idx,
                input_data=url,
                ground_truth="",
                type="url"
            ))

        dataset_dict['records'] = records
        dataset = Dataset.from_dict(dataset_dict)
        dataset.save()
        st.experimental_rerun()

# uploaded_dataset = st.file_uploader("Dataset to import:", type=["csv", "json"])
# if uploaded_dataset is not None:
#     bytes_data = uploaded_dataset.getvalue()
#     dataset_dict = json.loads(bytes_data)
#     st.json(dataset_dict)

#     dataset_name = st.text_input("Enter a dataset name:")
#     if st.button("Import"):
#         if dataset_name == '':
#             st.error('Dataset name cannot be empty')
#         else:
#             dataset_id = len(datasets)
#             dataset_dict['id'] = dataset_id
#             dataset_dict['name'] = dataset_name
#             dataset = Dataset.from_dict(dataset_dict)
#             dataset.save()
#             st.experimental_rerun()

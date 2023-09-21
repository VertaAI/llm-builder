import json
from typing import List

import streamlit as st

from computation import run_computations
from dataset.base import Dataset
from models.abc import Model
from models.nop import Nop
from prompts.base import Prompt
from table import load_data, create_table

INIT_SESSION_STATE = 'init_done'
_FORM_VALIDATION_KEY = 'dc_form_validation'


def init_session_state():
    st.session_state[INIT_SESSION_STATE] = True


if INIT_SESSION_STATE not in st.session_state:
    init_session_state()

models: List[Model] = [
    Nop(0),
]

# generate_data()
(datasets, prompts) = load_data()

st.set_page_config(layout="wide")

# Create a DataFrame from the sample data
st.title('LLM builder')

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
            (datasets, prompts) = load_data()

st.subheader('Prompt playground')
with st.form("playground", clear_on_submit=False):
    model_options = [model.get_name() for model in models]
    model_selection = st.selectbox('Select a model:', model_options)

    dataset_options = [dataset.name for dataset in datasets]
    dataset_selection = st.selectbox('Select a dataset:', dataset_options)

    if st.session_state.pop('prompt_name'+_FORM_VALIDATION_KEY, None):
        st.error('Prompt name cannot be empty')
    prompt_name = st.text_input('Enter a prompt name:', key='prompt_name')

    if st.session_state.pop('prompt_content'+_FORM_VALIDATION_KEY, None):
        st.error('Prompt content cannot be empty')
    prompt_content = st.text_area('Enter a prompt context:', height=200, key='prompt_content')

    f1, f2 = st.columns([0.1, 0.9])
    with f1:
        try_button = st.form_submit_button("Try prompt")
    with f2:
        save_button = st.form_submit_button("Save prompt")
    if try_button:
        if len(prompt_content) > 0 and len(prompt_name) > 0:
            model = [m for m in models if m.get_name() == model_selection][0]
            dataset = [d for d in datasets if d.name == dataset_selection][0]

            try_table = st.table(
                create_table([dataset], [model], [Prompt('', prompt_name, prompt_content)], cached=False))
        else:
            if len(prompt_name) == 0:
                st.session_state['prompt_name'+_FORM_VALIDATION_KEY] = True
            if len(prompt_content) == 0:
                st.session_state['prompt_content'+_FORM_VALIDATION_KEY] = True
            st.experimental_rerun()

    if save_button:
        if len(prompt_content) > 0 and len(prompt_name) > 0:
            model = [m for m in models if m.get_name() == model_selection][0]
            dataset = [d for d in datasets if d.name == dataset_selection][0]
            prompt_id = len(prompts)
            prompt = Prompt(prompt_id, prompt_name, prompt_content)
            prompt.save()
            run_computations(model, prompt, dataset)
            (datasets, prompts) = load_data()
            # TODO: clear rest of playground
        else:
            if len(prompt_name) == 0:
                st.session_state['prompt_name'+_FORM_VALIDATION_KEY] = True
            if len(prompt_content) == 0:
                st.session_state['prompt_content'+_FORM_VALIDATION_KEY] = True
            st.experimental_rerun()

st.subheader('LLM Library')

df = create_table(datasets, models, prompts, cached=True)
df_with_selections = df.copy()
df_with_selections.insert(0, "Select", False)
edited_df = st.data_editor(
    df_with_selections,
    hide_index=True,
    column_config={"Select": st.column_config.CheckboxColumn(required=True)},
    disabled=df.columns,
    width=10000,
)

selected_rows = edited_df[edited_df.Select]
selection = selected_rows.drop('Select', axis=1)
st.write("Selected rows:")
st.data_editor(
    selection,
    hide_index=True,
    disabled=df.columns,
    width=10000,
)


@st.cache_data
def convert_df(table):
    return table.to_csv(index=False).encode('utf-8')


# TODO: revisit the way that we are downloading. Remove columns? Save to json?
csv = convert_df(selection)

st.download_button(
    "Export selection",
    csv,
    "dataset.csv",
    "text/csv",
    key='download-csv'
)

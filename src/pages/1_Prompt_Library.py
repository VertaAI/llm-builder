import pandas as pd
import streamlit as st
from st_aggrid import GridOptionsBuilder, AgGrid, DataReturnMode, GridUpdateMode, ColumnsAutoSizeMode
from streamlit.errors import StreamlitAPIException

from table import load_data, create_table
from prompts.base import Prompt
from computation import run_computations
import LLM_Builder

_FORM_VALIDATION_KEY = 'dc_form_validation'
try:
    st.set_page_config(layout="wide")
except StreamlitAPIException:
    pass

models = LLM_Builder.load_models()
(datasets, prompts) = load_data()

st.subheader('Prompt Library')

prompt_frame = pd.DataFrame(prompts)
gb = GridOptionsBuilder.from_dataframe(prompt_frame)

gb.configure_default_column(groupable=True, value=True, enableRowGroup=True, autoHeight=True, wrapText=True)
gb.configure_selection(selection_mode="single", use_checkbox=False)
gb.configure_column("id", hide=True)
prompt_grid = AgGrid(
    prompt_frame,
    data_return_mode=DataReturnMode.AS_INPUT,
    update_mode=GridUpdateMode.SELECTION_CHANGED,
    columns_auto_size_mode=ColumnsAutoSizeMode.FIT_ALL_COLUMNS_TO_VIEW,
    gridOptions=gb.build(), height=500)

selected = prompt_grid["selected_rows"]
prompt = None
if len(selected) == 1:
    st.subheader('Update prompt')
    prompt = selected[0]
# st.write(prompt)

st.subheader('Prompt playground')
with st.form("playground", clear_on_submit=False):
    model_options = [model.get_name() for model in models]
    model_selection = st.selectbox('Select a model:', model_options)

    dataset_options = [dataset.name for dataset in datasets]
    dataset_selection = st.selectbox('Select a dataset:', dataset_options)

    if st.session_state.pop('prompt_content'+_FORM_VALIDATION_KEY, None):
        st.error('Prompt content cannot be empty')

    if prompt:
        prompt_content = st.text_area('Enter a prompt:', height=200, key='prompt_content', value=prompt['prompt'])
    else:
        prompt_content = st.text_area('Enter a prompt:', height=200, key='prompt_content')

    f1, f2 = st.columns([0.1, 0.9])
    with f1:
        try_button = st.form_submit_button("Try prompt")
    with f2:
        save_button = st.form_submit_button("Save prompt")
    if try_button:
        if len(prompt_content) > 0:
            model = [m for m in models if m.get_name() == model_selection][0]
            dataset = [d for d in datasets if d.name == dataset_selection][0]
            with st.spinner("Please wait..."):
                try_table = st.table(
                    create_table([dataset], [model], [Prompt(-1, prompt_content)], cached=False))
        else:
            if len(prompt_content) == 0:
                st.session_state['prompt_content'+_FORM_VALIDATION_KEY] = True
            st.experimental_rerun()

    if save_button:
        if len(prompt_content) > 0:
            model = [m for m in models if m.get_name() == model_selection][0]
            dataset = [d for d in datasets if d.name == dataset_selection][0]
            if prompt:
                prompt_id = prompt['id']
            else:
                prompt_id = len(prompts)
            prompt = Prompt(prompt_id, prompt_content)
            prompt.save()
            run_computations(model, prompt, dataset)
            (datasets, prompts) = load_data()
            st.info('Prompt and computations saved to the Library!')
            # TODO: clear rest of playground
            st.experimental_rerun()
        else:
            if len(prompt_content) == 0:
                st.session_state['prompt_content'+_FORM_VALIDATION_KEY] = True
            st.experimental_rerun()

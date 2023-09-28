import LLM_Builder
import pandas as pd
import streamlit as st
from st_aggrid import GridOptionsBuilder, AgGrid, DataReturnMode, GridUpdateMode, ColumnsAutoSizeMode
from streamlit.errors import StreamlitAPIException
from table import load_data

_FORM_VALIDATION_KEY = 'dc_form_validation'
try:
    st.set_page_config(page_title='Prompt Library', layout="wide")
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
    columns_auto_size_mode=ColumnsAutoSizeMode.FIT_CONTENTS,
    gridOptions=gb.build(), height=500)

# selected = prompt_grid["selected_rows"]
# prompt = None
# if len(selected) == 1:
#     st.subheader('Update prompt')
#     prompt = selected[0]

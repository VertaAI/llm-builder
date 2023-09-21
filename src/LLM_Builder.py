import streamlit as st
from typing import List
from models.nop import Nop
from models.abc import Model

st.set_page_config(page_title='LLM Builder', layout="wide")
st.write('# Build your LLM Application')
st.markdown('## Instructions')
st.markdown('* Point A')
st.markdown('* Point B')
st.markdown('* Point C')

st.sidebar.success("Activities")

models: List[Model] = [
    Nop(0),
]
st.session_state['models'] = models

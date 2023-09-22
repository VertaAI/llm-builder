import streamlit as st
from typing import List
from models.nop import Nop
from models.abc import Model

st.set_page_config(page_title='LLM Builder', layout="wide")
st.write('# Build your LLM Application')
st.markdown("""
## Instructions
  * Point A
  * Point B
  * Point C
""")


def load_models():
    models: List[Model] = [
        Nop(0),
    ]
    return models

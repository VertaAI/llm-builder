import streamlit as st
from typing import List
from models.nop import Nop
from models.abc import Model
from models.davinci import DaVinci

st.set_page_config(page_title='LLM Builder', layout="wide")

st.write('# Build your LLM Application')
st.markdown("""
## Instructions
  * If you are using OpenAI based models, add the OPENAI_API_KEY key to your environment variables and re-run the application.
  * Point B
  * Point C
""")


def load_models():
    models: List[Model] = [
        Nop(0), DaVinci(1)
    ]
    return models

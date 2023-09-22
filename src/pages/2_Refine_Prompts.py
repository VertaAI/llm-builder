import streamlit as st

from table import load_data, create_table
from prompts.base import Prompt
from computation import run_computations
import LLM_Builder

_FORM_VALIDATION_KEY = 'dc_form_validation'

models = LLM_Builder.load_models()
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
            st.info('Prompt and computations saved to the Library!')
            # TODO: clear rest of playground
        else:
            if len(prompt_name) == 0:
                st.session_state['prompt_name'+_FORM_VALIDATION_KEY] = True
            if len(prompt_content) == 0:
                st.session_state['prompt_content'+_FORM_VALIDATION_KEY] = True
            st.experimental_rerun()

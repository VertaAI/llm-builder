import os
from typing import List

import openai
import streamlit as st
from st_aggrid import AgGrid, ColumnsAutoSizeMode, GridOptionsBuilder

import computation
import table
from ai import Doc
from ai import refine_task_message_prompt
from dataset.base import Dataset
from models.abc import Model
from models.davinci import DaVinci
from models.chatgpt import ChatGPT
from models.chatgpt16k import ChatGPT16k
from prompts.base import Prompt
from table import load_data, load_config

st.set_page_config(page_title="LLM Builder", layout="wide")

_FORM_VALIDATION_KEY = "dc_form_validation"


def load_models():
    models: List[Model] = [DaVinci(1), ChatGPT(2), ChatGPT16k(3)]
    return models


openai.api_key = os.environ["OPENAI_API_KEY"]

models = load_models()
(datasets, prompts) = load_data()

# find the scratch dataset to write to
scratch_dataset: Dataset = next(filter(lambda x: x.name == "Scratch Dataset", datasets))

config = load_config()
if "prompts" not in st.session_state:
    st.session_state["prompts"] = []
    st.session_state["prompt_options"] = []
st.session_state["prompts"] = prompts
st.session_state["prompt_options"] = [
    prompt.get_name() for prompt in st.session_state["prompts"]
]

col1, col2 = st.columns([2, 2])
with col1:
    input_doc = None
    st.subheader("Document Summarization Bot")
    with st.container():
        input_method = st.selectbox(
            "Select input method", ("File", "URL", "Text", "Dataset")
        )
        if input_method == "File":
            # Upload a file
            uploaded_file = st.file_uploader("Upload a file (.txt)", type=["txt"])
            if uploaded_file is not None:
                input_doc = Doc.from_bytes(uploaded_file)
                st.text_area(label="Fetched Text", value=input_doc.content)
        elif input_method == "URL":
            url = st.text_input("Enter URL")
            if url:
                try:
                    input_doc = Doc.from_url(url)
                    st.text_area(label="Fetched Text", value=input_doc.content)
                except Exception as e:
                    st.write(f"Error: Unable to fetch data from the URL, {e}")
        elif input_method == "Text":
            input_text = st.text_area("Enter text")
            if input_text:
                input_doc = Doc.from_string(input_text)
        elif input_method == "Dataset":
            datasets = table.load_datasets()
            selected_dataset = st.selectbox(
                "Select a dataset", [dataset.name for dataset in datasets]
            )
        all_prompts = st.checkbox("Run all prompts")

        # "Summarize" button
        if st.button("Summarize"):
            model = next(
                filter(
                    lambda x: x.get_name() == st.session_state["model_selection"],
                    models,
                )
            )

            def single_prompt_prediction(selected_prompt, text):
                summary = model.predict(selected_prompt, text)
                st.subheader("Generated Summary")
                st.write(summary)
                # result = {"Id": ["abc"], "Input": [uploaded_file.name], "Prompt": [selected_prompt.prompt],
                #             "Output": [summary]}
                new_record = scratch_dataset.add_record(str(text))
                computation.write_result(
                    model, selected_prompt, scratch_dataset, new_record, summary
                )

            if input_method == "Dataset":
                dataset = next(filter(lambda ds: ds.name == selected_dataset, datasets))
                for record in dataset.records:
                    if not all_prompts:
                        selected_prompt = next(
                            filter(
                                lambda x: x.name
                                == st.session_state["prompt_selection"],
                                prompts,
                            )
                        )
                        single_prompt_prediction(selected_prompt, record.input_data)
                    else:
                        for selected_prompt in prompts:
                            single_prompt_prediction(selected_prompt, record.input_data)
            elif input_doc.content.strip():
                text = input_doc.content
                if input_doc.filename:
                    metadata = input_doc.filename
                elif input_doc.url:
                    metadata = input_doc.url
                else:
                    metadata = "raw_string"

                if not all_prompts:
                    selected_prompt = next(
                        filter(
                            lambda x: x.name == st.session_state["prompt_selection"],
                            prompts,
                        )
                    )
                    single_prompt_prediction(selected_prompt, text)
                else:
                    for selected_prompt in prompts:
                        single_prompt_prediction(selected_prompt, text)

with col2:
    st.subheader("Configuration")
    with st.expander("Model Configuration"):
        model_options = [model.get_name() for model in models]
        model_selection = st.selectbox(
            "Select a model:", model_options, key="model_selection"
        )

    # dataset_options = [dataset.name for dataset in datasets]
    # dataset_selection = st.selectbox('Select a dataset:', dataset_options)

    # def on_change_prompt_select():
    #     print("hello")
    #     print(st.session_state.prompt_name)

    with st.expander("Prompt Configuration"):
        prompt_selection = st.selectbox(
            "Current Prompt:",
            st.session_state["prompt_options"],
            key="prompt_selection",
        )

        prompt = next(
            filter(
                lambda x: x.get_name() == prompt_selection, st.session_state["prompts"]
            )
        )
        prompt = prompt.to_dict()

        # if st.session_state.pop('prompt_name'+_FORM_VALIDATION_KEY, None):
        #     st.error('Prompt name cannot be empty')

        # if prompt:
        #     # prompt_name = st.text_input('Name:', key='prompt_name', value=prompt['name'])
        #     prompt_description = st.text_input('Description:', key='prompt_desc', value=prompt['description'])
        # else:
        #     # prompt_name = st.text_input('Name:', key='prompt_name')
        #     prompt_description = st.text_input('Description:', key='prompt_desc')

        if st.session_state.pop("prompt_content" + _FORM_VALIDATION_KEY, None):
            st.error("Prompt content cannot be empty")
        if prompt:
            prompt_content = st.text_area(
                "Prompt Text:", height=200, key="prompt_content", value=prompt["prompt"]
            )
        else:
            prompt_content = st.text_area(
                "Prompt Text:", height=200, key="prompt_content"
            )

        save_button = st.button("Save as new prompt")
        if save_button:
            if len(prompt_content) > 0:
                prompt_id = len(prompts)
                prompt = Prompt(
                    prompt_id,
                    prompt["name"] + "-edited",
                    "Edited version of Prompt Id" + str(prompt["id"]),
                    prompt_content,
                )
                prompt.save()
                st.experimental_rerun()
            else:
                if len(prompt_content) == 0:
                    st.session_state["prompt_content" + _FORM_VALIDATION_KEY] = True
                st.experimental_rerun()

        st.markdown("<hr>", unsafe_allow_html=True)

        feedback = st.text_input("Provide feedback on the prompt")
        if st.button("Auto Refine Prompt"):
            # make call
            recommendation = refine_task_message_prompt(
                prompt_content, feedback
            ).strip()
            st.write(recommendation)
            if "auto_refine_rec" not in st.session_state:
                st.session_state["auto_refine_rec"] = recommendation

        if st.button("Add to prompt library"):
            prompt_id = len(prompts)
            prompt = Prompt(
                prompt_id,
                prompt["name"] + "-refined-" + "-".join(feedback.split(" ")),
                "Refined prompt using feedback: " + feedback,
                st.session_state["auto_refine_rec"],
            )
            prompt.save()
            st.session_state["prompts"].append(prompt)
            st.session_state["prompt_options"].append(prompt.get_name())
            st.experimental_rerun()
            print("hurray")

# results area
st.subheader("Recent Results")
df = table.read_results()[:5]

gb = GridOptionsBuilder.from_dataframe(df)
gb.configure_default_column(
    groupable=True, value=True, enableRowGroup=True, wrapText=True, autoHeight=False
)
gb.configure_column("record id", hide=True)
gb.configure_selection(selection_mode="multiple", use_checkbox=True)

library_grid = AgGrid(
    df,
    height=200,
    columns_auto_size_mode=ColumnsAutoSizeMode.FIT_CONTENTS,
    gridOptions=gb.build(),
    key="grid",
)
st.write("[See all results](/Results_Library)")

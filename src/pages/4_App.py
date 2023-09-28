import json
import os

import openai
import pandas as pd
import streamlit as st
from streamlit.errors import StreamlitAPIException
from ai import summarize, refine_task_message_prompt
from table import load_data, load_config, load_datasets
from ai import Doc

try:
    st.set_page_config(page_title="App", layout="wide")
except StreamlitAPIException:
    pass

openai.api_key = os.environ["OPENAI_API_KEY"]
(_, prompts) = load_data()
config = load_config()

# Create an initial dataframe
data = {"Id": [], "Input": [], "Prompt": [], "Output": []}
df = pd.DataFrame(data)
if "df" not in st.session_state:
    st.session_state["df"] = df


# Function to update the table with new data
def update_table(new_data):
    # Add new data to the dataframe
    df_new = pd.DataFrame(new_data)
    df_updated = pd.concat([st.session_state["df"], df_new], ignore_index=True)
    st.session_state["df"] = df_updated


# Streamlit app title
st.title("Document Summarization Bot")

logs = open("logs.json", "a")

input_method = st.selectbox("Select input method", ("File", "URL", "Text", "Dataset"))

if input_method == "File":
    # Upload a file
    uploaded_file = st.file_uploader("Upload a file (.txt)", type=["txt"])
    if uploaded_file is not None:
        if (
            uploaded_file.type
            == "application/vnd.openxmlformats-officedocument.wordprocessingml.document"
        ):
            # Convert .docx to text
            # text = docx2txt.process(uploaded_file)
            pass
        else:
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
    datasets = load_datasets()
    selected_dataset = st.selectbox("Select a dataset", [dataset.name for dataset in datasets])
prompt_name = config["prompt"]

# "Summarize" button
if st.button("Summarize"):
    if input_method == "Dataset":
        dataset = next(filter(lambda ds: ds.name == selected_dataset, datasets))
        selected_prompt = next(filter(lambda x: x.name == prompt_name, prompts))
        for record in dataset.records:
            summary = summarize(record.input_data, prompt=selected_prompt.prompt)
            result = {
                "Id": ["abc"],
                "Input": [record.input_data],
                "Prompt": [selected_prompt.prompt],
                "Output": [summary],
            }
            update_table(result)
    elif input_doc.content.strip():
        text = input_doc.content
        if input_doc.filename:
            metadata = input_doc.filename
        elif input_doc.url:
            metadata = input_doc.url
        else:
            metadata = "raw_string"
        # call AI model
        selected_prompt = next(filter(lambda x: x.name == prompt_name, prompts))
        summary = summarize(text, prompt=selected_prompt.prompt)

        st.write(f"Summary:\n {summary}")
        result = {
            "Id": ["abc"],
            "Input": [metadata],
            "Prompt": [selected_prompt.prompt],
            "Output": [summary],
        }
        update_table(result)
    else:
        st.warning("Please provide an input.")

st.write("Experimentation Trace")
st.table(st.session_state["df"])
# st.button("Analyze with Verta")

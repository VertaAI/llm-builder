import json
import os

import openai
import pandas as pd
import streamlit as st
from ai import summarize, refine_task_message_prompt
from table import load_data

try:
    st.set_page_config(page_title='App', layout="wide")
except StreamlitAPIException:
    pass

openai.api_key = os.environ["OPENAI_API_KEY"]
(_, prompts) = load_data()

# Create an initial dataframe
data = {'Id': [],
        'Input': [],
        'Prompt': [],
        'Output': []}
df = pd.DataFrame(data)
if 'df' not in st.session_state:
    st.session_state['df'] = df


# Function to update the table with new data
def update_table(new_data):
    # Add new data to the dataframe
    df_new = pd.DataFrame(new_data)
    df_updated = pd.concat([st.session_state['df'], df_new], ignore_index=True)
    st.session_state['df'] = df_updated

    # Display the updated table
    # st.table(st.session_state['df'])


# Streamlit app title
st.title("Document Summarization Bot")

logs = open("logs.json", "a")

# Upload a file
uploaded_file = st.file_uploader("Upload a file (.txt)", type=["txt"])

prompt_name = st.selectbox("Select a prompt", options=[item.name for item in prompts], index=0)

# "Summarize" button
if st.button("Summarize"):
    if uploaded_file is not None:
        # Check if the uploaded file is a .docx file
        if uploaded_file.type == "application/vnd.openxmlformats-officedocument.wordprocessingml.document":
            # Convert .docx to text
            # text = docx2txt.process(uploaded_file)
            pass
        else:
            # Read text from the uploaded .txt file
            text = uploaded_file.read()
            # call AI model
            selected_prompt = next(filter(lambda x: x.name == prompt_name, prompts))
            summary = summarize(text, prompt=selected_prompt.prompt)

            st.write(f"Summary:\n {summary}")
            result = {"Id": ["abc"], "Input": [uploaded_file.name], "Prompt": [selected_prompt.prompt],
                      "Output": [summary]}
            update_table(result)
            logs.write(json.dumps(result) + "\n")
    else:
        st.warning("Please upload a file first.")

feedback = st.text_input("Provide feedback on the prompt")

if st.button("Auto Refine Prompt"):
    # make call
    current_prompt = next(filter(lambda x: x['name'] == prompt_name, prompts))["task_message"]
    recommendation = refine_task_message_prompt(current_prompt, feedback)
    st.write("Recommendation:")
    st.write(recommendation)
    pass

if st.button("Add to prompt library"):
    pass

st.write('Experimentation Trace')
st.table(st.session_state['df'])
st.button("Analyze with Verta")

import streamlit as st

import table
models = st.session_state['models']

(datasets, prompts) = table.load_data()
df = table.create_table(datasets, models, prompts, cached=True)
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

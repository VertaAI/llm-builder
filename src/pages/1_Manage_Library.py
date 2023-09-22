import pandas as pd
import streamlit as st

import table
from st_aggrid import AgGrid, ColumnsAutoSizeMode, ExcelExportMode, GridOptionsBuilder

models = st.session_state['models']

(datasets, prompts) = table.load_data()
df = table.create_table(datasets, models, prompts, cached=True)
df_with_selections = df.copy()
df_with_selections.insert(0, "Select", False)

gb = GridOptionsBuilder.from_dataframe(df)
gb.configure_default_column(groupable=True, value=True, enableRowGroup=True, wrapText=True, autoHeight=True)
gb.configure_selection(selection_mode="multiple", use_checkbox=True)
library_grid = AgGrid(df, height=500, columns_auto_size_mode=ColumnsAutoSizeMode.FIT_ALL_COLUMNS_TO_VIEW, gridOptions=gb.build(), key='grid')

selected_rows = library_grid["selected_rows"]
selection = pd.DataFrame(selected_rows)
# TODO: this isn't working as expected. The column is not being dropped.
if '_selectedRowNodeInfo' in selection.columns:
    selection.drop(labels='_selectedRowNodeInfo', axis=1)
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

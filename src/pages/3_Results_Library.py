import json
import os
from enum import Enum

import LLM_Builder
import pandas as pd
import streamlit as st
import table
from st_aggrid import AgGrid, ColumnsAutoSizeMode, GridOptionsBuilder
from streamlit.errors import StreamlitAPIException
from verta import Client

try:
    st.set_page_config(page_title='Results Library', layout="wide")
except StreamlitAPIException:
    pass

models = LLM_Builder.load_models()

col1, col2, col3 = st.columns([1,5,2])

with col3:
    # analyze_button = st.button("Analyze with Verta")
    pass
with col1:
    st.subheader('Results')

(datasets, prompts) = table.load_data()


df = table.read_results()

gb = GridOptionsBuilder.from_dataframe(df)
gb.configure_default_column(groupable=True, value=True, enableRowGroup=True, wrapText=True, autoHeight=True)
gb.configure_column("record id", hide=True)
gb.configure_selection(selection_mode="multiple", use_checkbox=True)

library_grid = AgGrid(df, height=500, columns_auto_size_mode=ColumnsAutoSizeMode.FIT_CONTENTS,
                      gridOptions=gb.build(), key='grid')

selected_rows = library_grid["selected_rows"]
selection = pd.DataFrame(selected_rows)

st.write("Selected rows:")
st.data_editor(
    selection,
    hide_index=True,
    disabled=df.columns,
    width=10000,
)



class EvaluationAttributeKey(Enum):
    MODEL_ID = '__VERTA_EVALUATION_MODEL_ID',  # attribute key for model/pipeline identifier
    CONFIGURATION = '__VERTA_EVALUATION_CONFIGURATION',  # attribute key for configuration
    HEADERS = '__VERTA_EVALUATION_HEADERS',  # attribute key for metadata for headers
    ROW = '__VERTA_EVALUATION_ROW',  # part of attribute key used to map file rows into attribute value


class EvaluationHeaderKey(Enum):
    ID = '__VERTA_HEADER_ID',  # verta's internal identifier for single row (id column at evaluations table)
    RESULT = '__VERTA_HEADER_RESULT',  # user result for single row (aprove/reject column at evaluations table)
    LABELS = '__VERTA_HEADER_LABELS',  # user labeling for single row (labels column at evaluations table)
    FEEDBACK = '__VERTA_HEADER_FEEDBACK',  # user feedback for single row (feedback column at evaluations table)


def duplicate_reserved_columns(df):
    reserved = ["input", "output", "groundtruth", "trace"]
    header_row = []
    originalColNames = df.columns.values.tolist()

    for idx, origColName in enumerate(originalColNames):
        processedName = origColName.lower().strip()
        if processedName in reserved:
            if processedName == origColName:
                header_row.append({
                    "columnNumber": idx,
                    "originalValue": origColName,
                    "value": processedName,
                    "isReserved": True
                })
            else:
                df[processedName] = df[origColName]
                header_row.append({
                    "columnNumber": idx,
                    "originalValue": origColName,
                    "value": processedName,
                    "isReserved": True
                })
        else:  # not reserved
            processedName += " (Metadata)"
            df[processedName] = df[origColName]
            header_row.append({
                "columnNumber": idx,
                "originalValue": origColName,
                "value": processedName,
                "isReserved": False
            })
    return header_row


def create_eval(
        name,  # rmv name
        evaluation_project,  # string; // registeredModelId
        filepath,  # filename
        description=None,  # string;
        labels=None,  # potential labels; -- NOTE: we need to allow label changes
        model_id=None,  # string; EvaluationAttributeKey.CONFIGURATION
        configuration=None  # string; // EvaluationAttributeKey.MODEL_ID
):
    # connect to Verta
    client = Client(
        host=os.environ.get("VERTA_HOST", 'app.verta.ai'),
        email=os.environ["VERTA_EMAIL"],
        dev_key=os.environ["VERTA_DEV_KEY"],
    )
    client._conn._set_default_workspace("Default")

    eval_rm = client.get_or_create_registered_model(name=evaluation_project, labels=['__VERTA_EVALUATION'])
    eval_rmv = None
    try:
        eval_rmv = eval_rm.get_version(name)
    except:
        pass
    finally:
        if eval_rmv:
            eval_rmv.delete()
    eval_rmv = eval_rm.create_version(name=name, desc=description, labels=labels)
    df = pd.read_csv(filepath, keep_default_na=False)
    header_row = duplicate_reserved_columns(df)
    eval_rmv.add_attributes({
        EvaluationAttributeKey.CONFIGURATION.value[0]: configuration,
        EvaluationAttributeKey.MODEL_ID.value[0]: model_id,
        EvaluationAttributeKey.HEADERS.value[0]: json.dumps(header_row)
    })
    eval_rmv.log_artifact("eval_file", filepath)
    for index, row in df.iterrows():
        index_plus_1 = index + 1
        processed_row = row.to_dict()
        processed_row[EvaluationHeaderKey.ID.value[0]] = index_plus_1
        processed_row[EvaluationHeaderKey.LABELS.value[0]] = []
        processed_row[EvaluationHeaderKey.FEEDBACK.value[0]] = ''
        # processed_row[EvaluationHeaderKey.RESULT.value[0]] = ''
        eval_rmv.add_attribute(EvaluationAttributeKey.ROW.value[0] + "_" + str(index_plus_1),
                               json.dumps(processed_row))
    return eval_rmv


if st.button("Analyze with Verta"):
    toexport = df
    if selection.shape[0] > 0:
        toexport = selection
        toexport.drop(labels=['_selectedRowNodeInfo'], axis=1, inplace=True)
    with st.spinner("Please wait..."):
        import time

        time_str = str(time.time_ns())
        rmvs = []
        sample_url = None
        for group in toexport.groupby(by=["model", "prompt", "dataset"]):
            full_promt = next(
                filter(lambda x: str(x.id) == str(group[0][1]), prompts))
            prompt_content = full_promt.prompt

            full_dataset = next(
                filter(lambda x: str(x.id) == str(group[0][2]), datasets))
            
            eval_id_human_readable = "-".join([
                group[0][0], 
                "_".join(full_promt.name.split()), 
                "_".join(full_dataset.name.split())])
            eval_name = "eval--" + eval_id_human_readable
            eval_df = group[1]
            eval_df = eval_df.drop(["model", "prompt", "dataset"], axis=1)
            if not os.path.exists("evaluations"):
                os.makedirs("evaluations")

            filename = "evaluations/" + eval_name + "--" + time_str + ".csv"
            eval_df.to_csv(open(filename, "w"), index=False)
            rmv = create_eval(
                eval_name,  # rmv name
                "Doc-Summarization",  # string
                filename,  # filename
                description="Evaluation for " + eval_id_human_readable,  # string;
                labels=["too short", "too long", "hallucination"], # potential labels;
                model_id=group[0][0],  # string; EvaluationAttributeKey.CONFIGURATION
                configuration=prompt_content  # string; // EvaluationAttributeKey.MODEL_ID
            )
            rmvs.append(rmv.id)
            sample_url = rmv.url
        compare_url = sample_url.split('registry')[0] + "evaluations/compare/" + "%2C".join([str(rmv) for rmv in rmvs])
    st.write("[Click here](" + compare_url + ")")
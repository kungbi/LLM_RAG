import os
import streamlit as st
from utils import opensearch_api
from utils import doc_extract_api
from utils.db_api import DBAPI, DB_Configuration

db_api = None

if "session_list" not in st.session_state:
    st.session_state.session_list = [1]

with st.sidebar:

    option = st.selectbox(
        "Select Chat",
        st.session_state.session_list,
        index=0,
        placeholder="Select chat..."
    )

    for chat in st.session_state.session_list:
        st.write(f"Chat {chat}")

    current_tab = option


    # 메인 영역에 현재 선택된 채팅 표시


if f"db_api_{current_tab}" in st.session_state:
    db_api: DBAPI = st.session_state[f"db_api_{current_tab}"]
    db_configs = db_api.get_configurations()

def extract(id: int):
    try:
        db_info = db_api.get_configuration(id)
        doc_extract_api.start_extract(db_info)
        st.session_state["extracted"] = True
    except:
        st.session_state["extracted"] = False

def display_file_content(file_path):
    with open(file_path, "r") as file:
        content = file.read()
    st.text(content)


def get_file_size(file_path):
    size = os.path.getsize(file_path)

    for unit in ["B", "KB", "MB", "GB"]:
        if size < 1024:
            return f"{size:.2f} {unit}"
        size /= 1024


def main():

    st.title("DB Schema Extraction")

    st.write(f"Current Chat: {current_tab}")

    db_error = False
    if db_api == None:
        db_error = True
    else:
        db_configs = db_api.get_configurations()
        if not db_configs:
            db_error = True
    if db_error:
        st.error(
            "No database configurations found. Please add a configuration in the config page."
        )
        return

    config_options = {
        f"Configuration {id + 1} - {config.database_name}": id
        for id, config in db_configs
    }
    selected_config = list(config_options.keys())[-1]

    doc_selection_options = [":rainbow[**Uploaded document**]", "**Extracted schema**"]
    doc_selection_options_dict = {key: i for i, key in enumerate(doc_selection_options)}
    doc_selection_option_start = doc_selection_options_dict[
        st.session_state['doc_selection']] if 'doc_selection' in st.session_state else 0

    st.session_state[f'doc_selection_{current_tab}'] = st.sidebar.radio(
        "Which document do you want to use?",
        doc_selection_options,
        captions=[
            "Documents uploaded from the Upload page.",
            "Schema documents extracted from DB schema.",
        ],
        disabled=True if f"extracted_{current_tab}" not in st.session_state or st.session_state == False else False,
        index=doc_selection_option_start
    )

    st.button(
        "Start Extract",
        type="secondary",
        use_container_width=True,
        on_click=extract,
        args=(config_options[selected_config],),
    )

    if f"extracted_{current_tab}" not in st.session_state or st.session_state == False:
        return

    schema_files = doc_extract_api.get_schema_list()

    selected_file = st.selectbox("Select a file to view its content", schema_files)

    if selected_file:
        script_dir = os.path.dirname(os.path.abspath(__file__))
        output_dir = os.path.join(script_dir, "../../schema")
        file_path = os.path.join(output_dir, selected_file)
        file_size = get_file_size(file_path)

        st.write(f"Selected File: {selected_file} - {file_size}")

        st.divider()
        display_file_content(file_path)
        st.divider()




main()

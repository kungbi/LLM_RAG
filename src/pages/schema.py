import os
import streamlit as st
from utils import opensearch_api
from utils import doc_extract_api
from utils.db_api import DBAPI, DB_Configuration

db_api = None

# 세션 초기화
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

# 선택된 채팅에 따라 DBAPI 객체 불러오기
if f"db_api_{current_tab}" in st.session_state:
    db_api: DBAPI = st.session_state[f"db_api_{current_tab}"]
    db_configs = db_api.get_configurations()

def extract(id: int):
    try:
        db_info = db_api.get_configuration(id)
        doc_extract_api.start_extract(db_info,current_tab)
        st.session_state[f"extracted_{current_tab}"] = True
    except:
        st.session_state[f"extracted_{current_tab}"] = False

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
    if db_api is None:
        db_error = True
    else:
        db_configs = db_api.get_configurations()
        if not db_configs:
            db_error = True

    if db_error:
        st.error("No database configurations found. Please add a configuration in the config page.")
        return

    # DB 설정 옵션 만들기
    config_options = {
        f"Configuration {id + 1} - {config.database_name}": id
        for id, config in db_configs
    }
    selected_config = list(config_options.keys())[-1]

    doc_selection_options = [":rainbow[**Uploaded document**]", "**Extracted schema**"]
    doc_selection_options_dict = {key: i for i, key in enumerate(doc_selection_options)}
    doc_selection_option_start = doc_selection_options_dict.get(
        st.session_state.get('doc_selection'), 0
    )

    st.session_state[f'doc_selection_{current_tab}'] = st.sidebar.radio(
        "Which document do you want to use?",
        doc_selection_options,
        captions=[
            "Documents uploaded from the Upload page.",
            "Schema documents extracted from DB schema.",
        ],
        disabled=True if not doc_extract_api.get_schema_list(f"./conv/Chat_{current_tab}/schema") else False,
        index=doc_selection_option_start
    )

    st.button(
        "Start Extract",
        type="secondary",
        use_container_width=True,
        on_click=extract,
        args=(config_options[selected_config],),
    )

    # if not st.session_state.get(f"extracted_{current_tab}"):
    #     return

    schema_files = doc_extract_api.get_schema_list(f"./conv/Chat_{current_tab}/schema")

    selected_file = st.selectbox("Select a file to view its content", schema_files)

    if selected_file:
        # ./conv/Chat_{current_tab}/schema 경로 설정
        script_dir = os.path.dirname(os.path.abspath(__file__))
        output_dir = os.path.join(f"./conv/Chat_{current_tab}/schema")
        file_path = os.path.join(output_dir, selected_file)
        file_size = get_file_size(file_path)

        st.write(f"Selected File: {selected_file} - {file_size}")
        st.divider()
        display_file_content(file_path)
        st.divider()



main()

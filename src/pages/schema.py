import os
import streamlit as st
from utils import opensearch_api
from utils import doc_extract_api
from utils.db_api import DBAPI, DB_Configuration

db_api: DBAPI = st.session_state.db_api


def extract(id: int):
    db_info = db_api.get_configuration(id)

    doc_extract_api.start_extract(db_info)


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

    db_configs = db_api.get_configurations()
    if not db_configs:
        st.error(
            "No database configurations found. Please add a configuration in the config page."
        )
        return
    config_options = {
        f"Configuration {id + 1} - {config.database_name}": id
        for id, config in db_configs
    }
    selected_config = st.sidebar.selectbox(
        "Select Database Configuration", options=list(config_options.keys())
    )

    print()

    st.session_state["db_schema_toggle"] = st.toggle(
        "Include in Opensearch",
        value=(
            st.session_state["db_schema_toggle"]
            if "db_schema_toggle" in st.session_state
            else False
        ),
    )
    st.button(
        "Start Extract",
        type="secondary",
        use_container_width=True,
        on_click=extract,
        args=(config_options[selected_config],),
    )

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

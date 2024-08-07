import os
import streamlit as st
from utils import opensearch_api
from utils import doc_extract_api


# Function to extract the schema
def extract():
    doc_extract_api.start_extract()


# Function to display the content of a selected file
def display_file_content(file_path):
    with open(file_path, "r") as file:
        content = file.read()
    st.text(content)


# Function to get file size
def get_file_size(file_path):
    size = os.path.getsize(file_path)
    # Convert size to human-readable format
    for unit in ["B", "KB", "MB", "GB"]:
        if size < 1024:
            return f"{size:.2f} {unit}"
        size /= 1024


def main():
    # Page title
    st.title("DB Schema Extraction")

    db_api = st.session_state.db_api
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

    on = st.toggle("Include in Opensearch")
    st.button(
        "Start Extract", type="secondary", use_container_width=True, on_click=extract
    )

    # List the schema files
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

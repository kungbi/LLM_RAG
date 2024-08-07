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


# Page title
st.title("DB Schema Extraction")
on = st.toggle("Include in Opensearch")
st.button("Start Extract", type="secondary", use_container_width=True, on_click=extract)

# List the schema files
schema_files = doc_extract_api.get_schema_list()
max_width = 600
st.write(f"<div style='max-width: {max_width}px;'>", unsafe_allow_html=True)

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
    # with st.expander(f"Content of {selected_file}"):

st.write("</div>", unsafe_allow_html=True)

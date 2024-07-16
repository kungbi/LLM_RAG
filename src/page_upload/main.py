import streamlit as st
import os
import sys
from langchain_text_splitters.character import CharacterTextSplitter
from src.utils import opensearch_api
import PyPDF2
import pandas as pd
import json


index_name = "application"
opensearch = opensearch_api.get_client()
opensearch.create_index(index_name)


# 파일 읽기 함수
def read_file(file):
    if file.type == "text/plain":
        return file.read().decode("utf-8")
    elif file.type == "application/pdf":
        pdf_reader = PyPDF2.PdfReader(file)
        return "".join([page.extract_text() for page in pdf_reader.pages])
    elif file.type == "text/csv":
        df = pd.read_csv(file)
        return df.to_string()
    return ""


# 텍스트를 청크로 분할하는 함수
def chunk_sentences(text, chunk_size=300, chunk_overlap=300):
    text_splitter = CharacterTextSplitter(
        chunk_size=chunk_size, chunk_overlap=chunk_overlap
    )
    return text_splitter.split_text(text)


# 데이터 디렉토리가 없으면 생성
if not os.path.exists("data"):
    os.makedirs("data")

# 파일 업로더
with st.form("my-form", clear_on_submit=True):
    files = st.file_uploader(
        "FILE UPLOADER",
        type=["csv", "txt", "pdf"],
        accept_multiple_files=True,
        label_visibility="collapsed",
        key="file_uploader",
    )
    submitted = st.form_submit_button("UPLOAD!")


def makefile_json(json_file):
    if not os.path.exists(json_file):
        with open(json_file, "w") as file:
            file.write("[]")


def read_file_json():
    json_file = "./data/uploaded_list.json"
    makefile_json(json_file)
    with open(json_file, "r") as file:
        text = file.read()
    data = json.loads(text)
    return data


def add_file_json(filename):
    json_file = "./data/uploaded_list.json"
    makefile_json(json_file)
    with open(json_file, "r") as file:
        text = file.read()
    data = json.loads(text)
    data.append(filename)
    with open(json_file, "w") as file:
        file.write(json.dumps(data))


def delete_file_json(filename):
    json_file = "./data/uploaded_list.json"
    makefile_json(json_file)
    with open(json_file, "r") as file:
        text = file.read()
    data = json.loads(text)
    data.remove(filename)
    with open(json_file, "w") as file:
        file.write(json.dumps(data))


if submitted and files is not None:
    uploaded = []
    not_uploaded = []

    for uploaded_file in files:
        if uploaded_file.name in read_file_json():
            not_uploaded.append(uploaded_file.name)
            continue
        add_file_json(uploaded_file.name)
        text = read_file(uploaded_file)
        chunks = chunk_sentences(text)
        for i, chunk in enumerate(chunks):
            embedding = opensearch.encode(chunk)
            action = {
                "filename": uploaded_file.name,
                "chunk": chunk,
                "embedding": embedding,
            }
            opensearch.index_document(index_name, f"{uploaded_file.name}_{i}", action)
        uploaded.append(uploaded_file.name)
    if uploaded:
        st.success(
            f"{', '.join([filename for filename in uploaded])} file has been added."
        )
    if not_uploaded:
        st.error(
            f"{', '.join([filename for filename in not_uploaded])} file alreay exists"
        )


# 파일 리스트 표시 및 삭제
def delete_file(file_name):
    delete_file_json(file_name)
    delete_query = {"query": {"term": {"filename": filename}}}

    client = opensearch.get_client()
    client.delete_by_query(index=index_name, body=delete_query)
    st.experimental_rerun()


st.write("List of uploaded files:")
for i, filename in enumerate(read_file_json()):
    col1, col2 = st.columns([0.85, 0.15])
    with col1:
        st.write(filename)
    with col2:
        if st.button("delete", key=f"delete_{i}"):
            delete_file(filename)

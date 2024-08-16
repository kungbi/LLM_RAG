import streamlit as st
import os
from utils import opensearch_api
import PyPDF2
import pandas as pd
import json
from env.opensearch_env import INDEX_NAME

# OpenSearch 연결
if "opensearch" not in st.session_state:
    st.session_state.opensearch = opensearch_api.connect()

opensearch = st.session_state.opensearch
opensearch.create_index(INDEX_NAME)

# 세션 리스트 초기화
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
st.write(f"Current Chat: {current_tab}")

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
    elif file.type == "application/json":  # json
        data = file.read()
        return json.loads(data)
    return ""

# 데이터 디렉토리가 없으면 생성
def ensure_data_directory():
    data_dir = os.path.join("conv", f"Chat_{current_tab}", "data")
    if not os.path.exists(data_dir):
        os.makedirs(data_dir)
    return data_dir

# JSON 파일 생성 및 관리 함수
def makefile_json(json_file):
    if not os.path.exists(json_file):
        with open(json_file, "w") as file:
            file.write("[]")

def read_file_json():
    json_file = os.path.join(ensure_data_directory(), "uploaded_list.json")
    makefile_json(json_file)
    with open(json_file, "r") as file:
        text = file.read()
    data = json.loads(text)
    return data

def add_file_json(filename):
    json_file = os.path.join(ensure_data_directory(), "uploaded_list.json")
    makefile_json(json_file)
    with open(json_file, "r") as file:
        text = file.read()
    data = json.loads(text)
    data.append(filename)
    with open(json_file, "w") as file:
        file.write(json.dumps(data))

def delete_file_json(filename):
    json_file = os.path.join(ensure_data_directory(), "uploaded_list.json")
    makefile_json(json_file)
    with open(json_file, "r") as file:
        text = file.read()
    data = json.loads(text)
    data.remove(filename)
    with open(json_file, "w") as file:
        file.write(json.dumps(data))

# 파일 업로더
with st.form("my-form", clear_on_submit=True):
    files = st.file_uploader(
        "FILE UPLOADER",
        type=["csv", "txt", "pdf", "json"],
        accept_multiple_files=True,
        label_visibility="collapsed",
        key="file_uploader",
    )
    submitted = st.form_submit_button("UPLOAD!")

if submitted and files is not None:
    uploaded = []
    not_uploaded = []

    for uploaded_file in files:
        if uploaded_file.name in read_file_json():
            not_uploaded.append(uploaded_file.name)
            continue

        add_file_json(uploaded_file.name)
        text = read_file(uploaded_file)

        opensearch.index_document_chunk(INDEX_NAME, uploaded_file.name, text)

        save_path = os.path.join(ensure_data_directory(), uploaded_file.name)
        with open(save_path, "wb") as f:
            f.write(uploaded_file.getbuffer())

        uploaded.append(uploaded_file.name)
    if uploaded:
        st.success(
            f"{', '.join([filename for filename in uploaded])} file has been added."
        )
    if not_uploaded:
        st.error(
            f"{', '.join([filename for filename in not_uploaded])} file already exists"
        )

# 파일 리스트 표시 및 삭제
def delete_file(file_name):
    delete_query = {"query": {"term": {"filename": file_name}}}
    opensearch.get_client().delete_by_query(index=INDEX_NAME, body=delete_query)

    delete_file_json(file_name)
    file_to_delete = os.path.join(ensure_data_directory(), file_name)
    if os.path.exists(file_to_delete):
        os.remove(file_to_delete)
    st.experimental_rerun()

st.write("List of uploaded files:")
for i, filename in enumerate(read_file_json()):
    col1, col2 = st.columns([0.85, 0.15])
    with col1:
        st.write(filename)
    with col2:
        if st.button("delete", key=f"delete_{i}"):
            delete_file(filename)

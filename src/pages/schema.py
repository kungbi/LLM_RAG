import streamlit as st
from utils import opensearch_api
import os
import json

# del st.session_state["opensearch"]
# if not "opensearch" in st.session_state:
#     st.session_state.opensearch = opensearch_api.connect()
# opensearch = st.session_state.opensearch
opensearch = opensearch_api.connect()
opensearch.create_index2("application_tables")
opensearch.create_index2("application_columns")

# schema 디렉토리 생성
if not os.path.exists("schema"):
    os.makedirs("schema")

# 파일 업로드 및 삭제 상태 관리
tables_file_uploaded = os.path.exists("schema/tables_file.json")
columns_file_uploaded = os.path.exists("schema/columns_file.json")

# 페이지 제목
st.title("DB Schema Upload")

# table 파일 업로드
if not tables_file_uploaded:
    tables_file = st.file_uploader("Upload Tables File", type=["json"], key="tables")
    if tables_file is not None:
        path = os.path.join("schema", "tables_file.json")
        with open(path, "wb") as f:
            text = tables_file.read()
            f.write(text)
        data = json.loads(text)
        for line in data:
            opensearch.index_tables(json.dumps(line))
        st.experimental_rerun()
else:
    st.write("Tables file uploaded successfully.")
    if st.button("Delete Tables File"):
        os.remove(os.path.join("schema", "tables_file.json"))
        st.experimental_rerun()

# column 파일 업로드
if not columns_file_uploaded:
    columns_file = st.file_uploader("Upload Columns File", type=["json"], key="columns")
    if columns_file is not None:
        path = os.path.join("schema", "columns_file.json")
        with open(path, "wb") as f:
            text = columns_file.read()
            f.write(text)
        data = json.loads(text)
        for line in data:
            opensearch.index_column(json.dumps(line))
        st.experimental_rerun()
else:
    st.write("Columns file uploaded successfully.")
    if st.button("Delete Columns File"):
        os.remove(os.path.join("schema", "columns_file.json"))
        st.experimental_rerun()


# 검색 기능 추가
st.title("Search DB Schema")

search_query = st.text_input("Enter search query:")
if st.button("Search"):
    if search_query:
        tables_res = opensearch.search_tables(search_query)
        columns_res = opensearch.search_columns(search_query)

        tables = []
        for table in tables_res["hits"]["hits"]:
            data = json.loads(table["_source"]["document"])
            tables.append(
                (data["dataset_name"] + "." + data["table_name"], table["_score"])
            )

        columns = []
        for column in columns_res["hits"]["hits"]:
            data = json.loads(column["_source"]["document"])
            columns.append((data, column["_score"]))

        print(tables)
        print(columns)
        if tables:
            for result in tables:
                st.write(result)
        else:
            st.write("No results found.")

        if columns:
            for result in columns:
                st.write(result)
        else:
            st.write("No results found.")

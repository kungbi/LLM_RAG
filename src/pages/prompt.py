import streamlit as st
from utils.chatapi import ChatAPI
import utils.opensearch_api as opensearch_api
from utils.search_query import build_search_query
from utils.relevant_doc_api import merge_text_files
from env.opensearch_env import INDEX_NAME
from utils.text2sql import generate_sql_script
from tabulate import tabulate
import json


def main():
    st.title("💬 Llama3 7B")
    st.caption("🚀 A Streamlit chatbot powered by Llama3 7B")

    # st.session_state를 사용하여 history 상태 유지
    if "history" not in st.session_state:
        st.session_state.history = []

    if "client" not in st.session_state:
        st.session_state.client = ChatAPI(
            url="http://localhost:1234/v1",
            model="lmstudio-community/Meta-Llama-3-8B-Instruct-BPE-fix-GGUF",
        )

    if "messages" not in st.session_state:
        st.session_state.messages = []

    if "opensearch" not in st.session_state:
        st.session_state.opensearch = opensearch_api.connect()
    opensearch = st.session_state.opensearch

    # Display chat history
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            if message["role"] == "user":
                st.markdown(message["content"])
            else:
                content = message["content"]
                if content["result"]:
                    st.markdown("###### SQL")
                    st.code(content["query"], language="sql")

                    if content["sql"]:
                        st.markdown("###### SQL result")
                        st.code(content["sql_result"])
                    else:
                        st.error(content["message"])
                else:
                    st.error(content["message"])

    # Get DB configuration from session state (assumed to be set in config.py)
    if "db_api" not in st.session_state:
        st.error(
            "Database configuration not found. Please set up the database in the config page first."
        )
        return

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

    if prompt := st.chat_input():
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.markdown(prompt)

        # opensearch
        query = build_search_query(query_embedding=opensearch.encode(prompt))
        response = opensearch.search(INDEX_NAME, query)
        response = (
            response.get("aggregations", {})
            .get("group_by_filename", {})
            .get("buckets", [])
        )
        relev_docs = [data["key"] for data in response]
        text = merge_text_files(relev_docs, token_limit=4000)

        with st.chat_message("assistant"):
            sql_response = generate_sql_script(prompt, text)
            full_response = {}

            try:
                json_data = json.loads(sql_response)
                if not "query" in json_data:
                    raise Exception("no query in response.")

                full_response["result"] = True
                full_response["query"] = json_data["query"]
                st.markdown("###### SQL")
                st.code(full_response["query"], language="sql")

                db_execute_result = db_api.execute(
                    config_options[selected_config], json_data["query"]
                )
                if db_execute_result["result"] == True:
                    full_response["sql"] = True
                    sql_result = db_execute_result["sql_result"]

                    pretty_string = tabulate(
                        sql_result, headers="keys", tablefmt="psql"
                    )
                    st.markdown("###### SQL result")

                    full_response["sql_result"] = pretty_string
                    st.code(full_response["sql_result"], language="sql")
                else:
                    full_response["sql"] = False
                    full_response["message"] = db_execute_result["error"]

            except Exception as e:
                st.error(f"An error occurred: {e}")
                full_response["result"] = False
                full_response["message"] = f"An error occurred: {e}"

        message = {"role": "assistant", "content": full_response}
        st.session_state.messages.append(message)


main()

import streamlit as st
import utils.opensearch_api as opensearch_api
from utils.opensearch_query import build_search_query
from utils.docs_api import merge_text_files
from env.opensearch_env import INDEX_NAME
from tabulate import tabulate
from utils.text2sql import txt2sql
from utils.token_limit import TokenLimit
import env.llm_env as LLM_ENV


def main():
    st.title("💬 Text2SQL")
    st.caption("🚀 A Streamlit chatbot powered by Qwen2 7B")

    # st.session_state를 사용하여 history 상태 유지
    if "history" not in st.session_state:
        st.session_state.history = []

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
                    if content["sql"]:
                        st.markdown("###### SQL")
                        st.code(content["query"], language="sql")
                        st.markdown("###### SQL result")
                        st.code(content["sql_result"])
                    else:
                        st.markdown(content["message"])
                else:
                    st.markdown(content["message"])

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
        text = merge_text_files(relev_docs)

        with st.chat_message("assistant"):
            full_response = {}
            response = txt2sql(prompt, text, config_options[selected_config])

            if response["result"] == None:
                full_response["result"] = False
                full_response["message"] = "shit"

            sql_response = response["sql_script"]

            try:
                full_response["result"] = True

                db_execute_result = db_api.execute(
                    config_options[selected_config], sql_response
                )
                if db_execute_result["result"] == True:
                    full_response["query"] = sql_response
                    st.markdown("###### SQL")
                    st.code(full_response["query"], language="sql")

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
                    full_response["message"] = db_execute_result[
                        "error"
                    ]  # source of error message
                    st.markdown(db_execute_result["error"])

            except Exception as e:
                st.error(f"An error occurred: {e}")
                full_response["result"] = False
                full_response["message"] = f"An error occurred: {e}"

        message = {"role": "assistant", "content": full_response}
        st.session_state.messages.append(message)


main()

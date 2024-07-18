import streamlit as st
from utils.chatapi import ChatAPI
import utils.opensearch_api as opensearch_api
from utils.search_query import build_search_query
from utils.relevant_doc_api import merge_text_files
from env.opensearch_env import INDEX_NAME
from utils.text2sql import generate_sql_script,txt2sql
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
    client = st.session_state.client

    if "messages" not in st.session_state:
        st.session_state.messages = [
            {"role": "assistant", "content": "How can I help you?"}
        ]

    if "opensearch" not in st.session_state:
        st.session_state.opensearch = opensearch_api.connect()
    opensearch = st.session_state.opensearch

    # for msg in st.session_state.messages:
    #     st.chat_message(msg["role"]).write(msg["content"])

    # Display chat history
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

    # Get DB configuration from session state (assumed to be set in config.py)
    if "db_api" not in st.session_state:
        st.error("Database configuration not found. Please set up the database in the config page first.")
        return

    db_api = st.session_state.db_api

    # Get available DB configurations
    db_configs = db_api.get_configurations()
    if not db_configs:
        st.error("No database configurations found. Please add a configuration in the config page.")
        return

    # Create a dropdown for selecting DB configuration
    config_options = {f"Configuration {id} - {config.database_name}": id for id, config in db_configs}
    selected_config = st.selectbox("Select Database Configuration", options=list(config_options.keys()))
    selected_config_id = config_options[selected_config]

    if prompt := st.chat_input():

        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.markdown(prompt)

        # opeansearch
        query = build_search_query(query_embedding=opensearch.encode(prompt))
        response = opensearch.search(INDEX_NAME, query)
        response = (
            response.get("aggregations", {})
            .get("group_by_filename", {})
            .get("buckets", [])
        )
        relev_docs = [data["key"] for data in response]

        text, token_count = merge_text_files(relev_docs, token_limit=4000)

        print(text)

        response = txt2sql(prompt,text,selected_config_id)
        st.write(response)
        st.session_state.messages.append({"role": "assistant", "content": response})

        # generate_sql_script 함수 호출
        # response = generate_sql_script(prompt, text)
        # st.write(response)
        # st.session_state.messages.append({"role": "assistant", "content": response})
        #
        # if "query" in response:
        #     response_dict=json.loads(response)
        #     sql_query = response_dict["query"]
        #     def execute_sql():
        #         # Assume the first configuration (index 0) is used
        #         result = db_api.execute(selected_config_id, sql_query)
        #         if result["result"]:
        #             df = result["sql_result"]
        #             st.write("Query Result:")
        #             st.dataframe(df)
        #             st.session_state.messages.append({"role": "assistant",
        #                                               "content": f"Query executed successfully. Results:\n\n{df.to_markdown()}"})
        #         else:
        #             error_message = f"Error executing query: {result['error']}"
        #             st.error(error_message)
        #             st.session_state.messages.append({"role": "assistant", "content": error_message})
        #
        #     st.button("Execute SQL", on_click=execute_sql)
        # else:
        #     st.error("Failed to generate a valid SQL query.")
        #     st.session_state.messages.append(
        #         {"role": "assistant", "content": "Sorry, I couldn't generate a valid SQL query for your request."})

        # st.session_state.messages.append({"role": "user", "content": prompt})
        # st.chat_message("user").write(prompt)
        # with st.chat_message("assistant"):
        #     response = client.send_request_history_stream(prompt)
        #     placeholder = st.empty()
        #     full_response = ""
        #     for item in response:
        #         full_response += item
        #         placeholder.markdown(full_response)
        #     placeholder.markdown(full_response)
        # message = {"role": "assistant", "content": full_response}
        # st.session_state.messages.append(message)


main()

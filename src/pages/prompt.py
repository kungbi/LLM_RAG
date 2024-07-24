import pyodbc
import streamlit as st
import utils.opensearch_api as opensearch_api
from utils.opensearch_query import build_search_query
from utils.docs_api import merge_text_files
from env.opensearch_env import INDEX_NAME
from tabulate import tabulate
from utils.text2sql import txt2sql
from utils.token_limit import TokenLimit
import env.llm_env as LLM_ENV
from utils.history_api import ConversationManager
import json
from pyodbc import ProgrammingError



def main():
    st.title("💬 Text2SQL")
    st.caption("🚀 A Streamlit chatbot powered by Qwen2 7B")

    # st.session_state를 사용하여 history 상태 유지
    # if "history" not in st.session_state:
    #     st.session_state.history = []

    if "memory_manager" not in st.session_state:
        st.session_state.memory_manager = ConversationManager()
    memoryManager = st.session_state.memory_manager

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
                        st.markdown("##### SQL")
                        st.code(content["query"], language="sql")
                        st.markdown("##### SQL result")
                        st.code(content["sql_result"])
                    else:
                        st.markdown(f"##### SQL Execution Fail: {content["num"]}")
                        st.code(content["query"], language="sql")
                        st.markdown(content["message"])
                else:
                    st.markdown(f"##### SQL Generation Fail")
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
        context = memoryManager.get_full_conversation_history()
        print("chat history: ")
        memoryManager.print_conversation_history()

        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.markdown(prompt)
            memoryManager.add_message_to_memory(role="user", content=prompt) #add history

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

            response_generator = txt2sql(prompt, text, config_options[selected_config], context)
            num = 1

            for response in response_generator:
                full_response = {
                    "result": False,
                    "sql": False,
                    "query": "",
                    "sql_result": "",
                    "message": "",
                    "num": num
                }

                if response["result"] is False:
                    full_response["message"] = response["error_message"]
                    st.markdown(f"##### SQL Generation Fail {num}")
                    st.markdown(response["error_message"])
                else:
                    sql_response = response.get("sql_script")
                    full_response["query"] = sql_response
                    full_response["result"] = True

                    try:
                        db_execute_result = db_api.execute(
                            config_options[selected_config], sql_response
                        )

                        if db_execute_result["result"]:
                            full_response["sql"] = True
                            sql_result = db_execute_result["sql_result"]
                            pretty_string = tabulate(
                                sql_result, headers="keys", tablefmt="psql"
                            )
                            full_response["sql_result"] = pretty_string
                        else:
                            full_response["message"] = f"An error occurred: {db_execute_result["error"]}"

                    except Exception as e:
                        full_response["message"] = f"An error occurred: {e}"

                if full_response["sql"]:
                    st.markdown("##### SQL")
                    st.code(full_response["query"], language="sql")
                    st.markdown("##### SQL result")
                    st.code(full_response["sql_result"], language="sql")
                elif full_response["message"]:
                    st.markdown(f"##### SQL Execution Fail : {num}")
                    st.code(full_response["query"], language="sql")
                    st.markdown(full_response["message"])

                # 세션 상태에 메시지 추가
                message = {"role": "assistant", "content": full_response}
                st.session_state.messages.append(message)

                print(type(full_response))
                print("full_response:", full_response)

                if isinstance(full_response, dict):
                    # message 항목이 예외 객체인지 확인 후 문자열로 변환
                    if isinstance(full_response.get('message'), pyodbc.ProgrammingError):
                        full_response['message'] = str(full_response['message'])

                    # for item in full_response.items():
                        # print(item, type(item[1]))
                    full_response_str = json.dumps(full_response)
                else:
                    full_response_str = full_response

                memoryManager.add_message_to_memory(role="assistant",content=full_response_str)

                num += 1



main()

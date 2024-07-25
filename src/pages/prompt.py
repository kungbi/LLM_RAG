import pyodbc
import streamlit as st
import json
import re
import utils.opensearch_api as opensearch_api
from utils.opensearch_query import build_search_query
from utils.docs_api import merge_text_files
from env.opensearch_env import INDEX_NAME
from tabulate import tabulate
from utils.text2sql import txt2sql
from utils import answer
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

    tokenlimit = TokenLimit()
    if tokenlimit.is_available_history(memoryManager.get_full_conversation_history()):
        memoryManager.summarize_and_update_buffer()

    # Display chat history
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            if message["role"] == "user":
                st.markdown(message["content"])
            else:
                content = message["content"]
                if content["result"]:
                    st.markdown("##### SQL")
                    st.code(content["query"], language="sql")

                    if content["sql"]:

                        st.markdown("##### SQL result")
                        st.code(content["sql_result"])
                        st.markdown("##### Answer")
                        st.code(content["answer"], language="text")
                    else:
                        st.markdown(f"##### SQL Execution Fail: {content['num']}")
                        st.markdown(content["message"])
                else:
                    st.markdown(f"##### SQL Generation Fail")
                    st.markdown(content["message"])

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
        
        context = memoryManager.get_full_conversation_history()
        print("chat history: ")
        memoryManager.print_conversation_history()

        with st.chat_message("user"):
            st.markdown(prompt)
            memoryManager.add_user_message_to_memory(prompt)

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

        splited_text = tokenlimit.split_document_by_tokens(text)

        with st.chat_message("assistant"):

            response_generator = txt2sql(prompt, splited_text, config_options[selected_config], context)
            num = 1
            full_responses = []

            for response in response_generator:
                full_response = {
                    "result": False,
                    "sql": False,
                    "query": "",
                    "sql_result": "",
                    "message": "",
                    "num": num,
                    "answer": "",
                }

                if response["result"] is False:
                    full_response["message"] = response["error_message"]
                    st.markdown(f"##### SQL Generation Fail {num}")
                    st.markdown(response["error_message"])
                else:
                    sql_response = response.get("sql_script")
                    full_response["query"] = sql_response
                    full_response["result"] = True
                    st.markdown("##### SQL")
                    st.code(full_response["query"], language="sql")

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
                            st.markdown("##### SQL result")
                            st.code(full_response["sql_result"])

                            try:
                                answer_response = answer.generate_answer(
                                    prompt,
                                    full_response["query"],
                                    full_response["sql_result"],
                                )
                                print(answer_response)
                                full_response["answer"] = json.loads(answer_response)[
                                    "answer"
                                ]
                            except Exception as e:
                                pattern = r"\{[^{}]*\}"
                                match = re.search(pattern, answer_response)
                                if match:
                                    json_object_str = match.group(0)
                                    try:
                                        full_response["answer"] = json.loads(
                                            json_object_str
                                        )["answer"]
                                    except Exception as e:
                                        full_response["answer"] = (
                                            f"An error occurred: {e}"
                                        )
                                else:
                                    full_response["answer"] = f"An error occurred: {e}"
                            st.markdown("##### Answer")
                            st.code(full_response["answer"], language="text")

                        else:
                            full_response["message"] = f"An error occurred: {db_execute_result["error"]}"

                    except Exception as e:
                        full_response["message"] = f"An error occurred: {e}"

                if full_response["message"]:
                    st.markdown(f"##### SQL Execution Fail : {num}")
                    st.markdown(full_response["message"])

                full_responses.append(full_response)
                message = {"role": "assistant", "content": full_response}
                st.session_state.messages.append(message)

                num += 1

                # full_response_str = json.dumps(full_response)
            combined_response_str=json.dumps(full_responses)

            memoryManager.add_ai_response_to_memory(combined_response_str)



main()

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
import time
from utils.router_api import semantic_layer
from utils import prompts
from utils.chatapi import ChatAPI
from utils.conv_save_local import MessageManager
import os
import shutil



st.markdown(
    """
    <style>
        section[data-testid="stSidebar"] {
            width: 300px !important; # Set the width to your desired value
        }
    </style>
    """,
    unsafe_allow_html=True,
)



def main():
    st.title("💬 Text2SQL")
    st.caption(f"🚀 A Streamlit chatbot powered by {LLM_ENV.LLM_MODEL}")

    def get_chat_numbers(base_dir: str):
        chat_numbers = []
        try:
            # base_dir에 있는 디렉토리만 필터링
            folders = [folder for folder in os.listdir(base_dir) if os.path.isdir(os.path.join(base_dir, folder))]

            for folder in folders:
                # "Chat_"으로 시작하는 폴더 이름에서 숫자 부분만 추출
                if folder.startswith("Chat_"):
                    try:
                        # 숫자 추출 시도
                        number = int(folder.split("_")[1])
                        chat_numbers.append(str(number))
                    except (IndexError, ValueError):
                        # 예외 처리: 형식이 잘못된 경우 무시
                        continue
            return sorted(chat_numbers)  # 숫자를 정렬하여 반환
        except Exception as e:
            st.error(f"Failed to list directories: {e}")
            return []

    # 세션 초기화
    if "session_list" not in st.session_state:
        # ./conv/ 경로에서 Chat_ 폴더의 숫자만 가져오기
        conv_dir = "./conv"
        st.session_state.session_list = get_chat_numbers(conv_dir)

    with st.sidebar:
        def new_chat():
            new_chat_number = f"{(len(st.session_state.session_list) + 1)}"
            st.session_state.session_list.append(new_chat_number)
            st.session_state[f"messages_{new_chat_number}"] = []  # New chat 초기화
            st.session_state[f"memory_manager_{new_chat_number}"] = ConversationManager()

        st.button('New Chat', on_click=new_chat)

        def clear_chat():
            st.session_state[f"messages_{current_tab}"]=[]
            st.session_state[f"memory_manager_{current_tab}"] = ConversationManager()
            path=f"./conv/Chat_{current_tab}"
            for filename in os.listdir(path):
                file_path = os.path.join(path, filename)
                if os.path.isfile(file_path) or os.path.islink(file_path):
                    os.unlink(file_path)  # 파일 삭제
                elif os.path.isdir(file_path):
                    shutil.rmtree(file_path)

        st.button('Clear Chat', on_click=clear_chat)

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


    # st.session_state를 사용하여 history 상태 유지
    # if "history" not in st.session_state:
    #     st.session_state.history = []

    # MessageManager 인스턴스 생성
    message_manager = MessageManager()

    if f"memory_manager_{current_tab}" not in st.session_state:
        st.session_state[f"memory_manager_{current_tab}"] = ConversationManager()

    memoryManager = st.session_state[f"memory_manager_{current_tab}"]

    if f"messages_{current_tab}" not in st.session_state:
        st.session_state[f"messages_{current_tab}"] = message_manager.load_messages(str(current_tab))
        print("session empty")
    # st.session_state[f"messages_{current_tab}"] = message_manager.load_messages(str(current_tab))
    # print("session not empyty")

    print("message:", st.session_state[f"messages_{current_tab}"] )

    if "opensearch" not in st.session_state:
        st.session_state.opensearch = opensearch_api.connect()
    opensearch = st.session_state.opensearch
    # opensearch = opensearch_api.connect()
    INDEX = f"{INDEX_NAME}_{current_tab}"

    if "client" not in st.session_state:
        st.session_state.client = ChatAPI(url=LLM_ENV.LLM_URL, model=LLM_ENV.LLM_MODEL)
    client = st.session_state.client

    tokenlimit = TokenLimit()
    if not tokenlimit.is_available_history(memoryManager.get_full_conversation_history()):
        memoryManager.summarize_and_update_buffer()

    # Display chat history
    for message in st.session_state[f"messages_{current_tab}"]:
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

                elif content["gen_conv"]:
                    st.markdown('##### Answer')
                    st.write(content["gen_conv"])

                else:
                    st.markdown(f"##### SQL Generation Fail")
                    st.markdown(content["message"])

    if f"db_api_{current_tab}" not in st.session_state:
        st.error(
            "Database configuration not found. Please set up the database in the config page first."
        )
        return

    db_api = st.session_state[f"db_api_{current_tab}"]
    db_configs = db_api.get_configurations()
    if not db_configs:
        st.error(
            "No database configurations found. Please add a configuration in the config page."
        )
        return

    config_options={
        f"Configuration{id+1} - {config.database_name}": id
        for id, config in db_configs
    }
    selected_config=list(config_options.keys())[-1]
    # config_options = {
    #     f"Configuration {id + 1} - {config.database_name}": id
    #     for id, config in db_configs
    # }


    # selected_config = st.sidebar.selectbox(
    #     "Select Database Configuration", options=list(config_options.keys())
    # )
    #
    doc_selection_options = [":rainbow[**Uploaded document**]", "**Extracted schema**"]
    # doc_selection_options_dict = {key:i for i, key in enumerate(doc_selection_options)}
    # doc_selection_option_start = doc_selection_options_dict[st.session_state['doc_selection']] if 'doc_selection' in st.session_state else 0
    # st.session_state['doc_selection'] = st.sidebar.radio(
    #     "Which document do you want to use?",
    #     doc_selection_options,
    #     captions=[
    #         "Documents uploaded from the Upload page.",
    #         "Schema documents extracted from DB schema.",
    #     ],
    #     disabled=True if "extracted" not in st.session_state or st.session_state == False else False,
    #     index=doc_selection_option_start
    # )

    if prompt := st.chat_input():
        start_time = time.time()
        
        st.session_state[f"messages_{current_tab}"].append({"role": "user", "content": prompt})

        message_manager.save_message(str(current_tab), {"role": "user", "content": prompt})

        context = memoryManager.get_full_conversation_history()

        with st.chat_message("user"):
            st.markdown(prompt)
            memoryManager.add_user_message_to_memory(prompt)

        doc_selection = st.session_state[f'doc_selection_{current_tab}'] if 'doc_selection' in st.session_state else 0
        if doc_selection == doc_selection_options[0]:
            query = build_search_query(query_embedding=opensearch.encode(prompt))
            response = opensearch.search(INDEX, query)
            response = (
                response.get("aggregations", {})
                .get("group_by_filename", {})
                .get("buckets", [])
            )
            relev_docs = [data["key"] for data in response]
        else:
            response = opensearch.search_schema(prompt)
            relev_docs = [data["key"] for data in response]


        text = merge_text_files(relev_docs)

        splited_text = tokenlimit.split_document_by_tokens(text)

        with st.chat_message("assistant"):

            route = semantic_layer(prompt)

            if route.name == 'GeneralConversationRouter':
                prompt_template = prompts.generate_conversation(prompt)
                response = client.send_request(prompt_template)
                full_response = {
                    "result": False,
                    "sql": False,
                    "query": "",
                    "sql_result": "",
                    "message": "",
                    "num": -1,
                    "answer": "",
                    "gen_conv":"",
                    "explanation":""

                }

                try:
                    response_json = json.loads(response)
                except Exception as e:
                    pattern = r"\{[^{}]*\}"
                    match = re.search(pattern, response)
                    if match:
                        json_object_str = match.group(0)
                        try:
                            response_json = json.loads(json_object_str)
                        except Exception as e:
                            response_json = None

                gen_answer = response_json.get("answer")
                # print("response: ", answer)

                st.markdown("##### Answer")
                st.write(gen_answer)

                full_response["gen_conv"] = gen_answer

                message = {"role": "assistant", "content": full_response}
                st.session_state[f"messages_{current_tab}"].append(message)
                message_manager.save_message(str(current_tab), message)

                memoryManager.add_ai_response_to_memory(gen_answer)
                end_time = time.time()
                st.markdown("##### Time:")
                st.markdown(f"{round(end_time - start_time, 2)}s")

            else:
                response_generator = txt2sql(prompt, splited_text, config_options[selected_config], context, current_tab)
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
                        "explanation":"",
                        "gen_conv":""
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
                                    # print(answer_response)
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
                        st.markdown("##### Explanation:")
                        st.write(response.get("explanation")) # add explanation
                        full_response["explanation"] = response.get("explanation")

                    full_responses.append(full_response)
                    message = {"role": "assistant", "content": full_response}
                    st.session_state[f"messages_{current_tab}"].append(message)
                    message_manager.save_message(str(current_tab), message)

                    num += 1

                    # full_response_str = json.dumps(full_response)
                combined_response_str=json.dumps(full_responses)

                memoryManager.add_ai_response_to_memory(combined_response_str)
                end_time = time.time()
                st.markdown("##### Time:")
                st.markdown(f"{round(end_time - start_time, 2)}s")



main()

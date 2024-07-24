import requests
from utils.chatapi import ChatAPI
import streamlit as st
import json
import re
import env.llm_env as LLM_ENV
from utils import prompts

client = ChatAPI(url=LLM_ENV.LLM_URL, model=LLM_ENV.LLM_MODEL)


def generate_sql_script(query, text, context):
    # prompt_template = prompts.generate_sql_script(query, text)
    prompt_template = prompts.generate_sql_script(query, text, context)

    data = {
        "messages": [
            {"role": "system", "content": "You are a MSSQL expert."},
            {"role": "user", "content": prompt_template},
        ],
        "temperature": 0.0,
        "max_tokens": -1,
        "stream": True,  # 스트리밍 모드 활성화
    }

    try:
        response = client.send_request(str(data))
        return response

    except requests.exceptions.RequestException as e:
        print(f"Error: {e}")
        return None


def format_error_history(error_history):
    formatted = "===Error History\n"
    for entry in error_history:
        formatted += f"Attempt {entry['attempt']}:\n"
        formatted += f"SQL Script:\n{entry['sql_script']}\n\n"
        formatted += f"Error Message:\n{entry['error_message']}\n\n"
    return formatted.strip()


def refine_sql_script(question, text, error_history, context):
    formatted_error_history = format_error_history(error_history)

    prompt_template = prompts.generate_refine_sql_script(
        question, text, formatted_error_history, context
    )

    data = {
        "messages": [
            {"role": "system", "content": "You are a senior data analyst."},
            {"role": "user", "content": prompt_template},
        ],
        "temperature": 0.0,
        "max_tokens": -1,
        "stream": True,  # Set to True if you need streaming
    }

    try:
        response = client.send_request(str(data))
        return response

    except requests.exceptions.RequestException as e:
        print(f"Error: {e}")
        return None


def txt2sql(question, txt, id, context):
    max_attempts = 2
    attempts = 0
    error_history = []
    sql_script = ""

    db_api = st.session_state.db_api

    while attempts < max_attempts:
        if attempts == 0:
            response = generate_sql_script(question, txt, context)
        else:
            print("text2sql retry")
            response = refine_sql_script(question, txt, error_history, context)
        # print(response)

        if response is None:
            yield {
                "result": False,
                "sql_script": None,
                "error_message": "Error in generating SQL Script",
            }
            attempts += 1
            continue

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
            else:
                print("No JSON object found.")
                yield {
                    "result": False,
                    "sql_script": None,
                    "error_message": "Failed to parse JSON response",
                }
                attempts += 1
                continue

        try:
            sql_script = response_json.get("query") or response_json.get(
                "refined_query"
            )

            if not sql_script:
                raise Exception("No SQL script found in response")

            sql_result = db_api.execute(id, sql_script)
            # print("db response:", sql_result)
            if sql_result["result"] == False:
                raise Exception(sql_result["error"])

            yield {
                "result": True,
                "sql_script": sql_script,
                "error_message": None,
            }
            return  # 성공 시 함수 종료

        except Exception as e:
            error_message = str(e)
            error_history.append(
                {
                    "attempt": attempts + 1,
                    "sql_script": sql_script,
                    "error_message": error_message,
                }
            )

            yield {
                "result": True,
                "sql_script": sql_script,
                "error_message": error_message,
            }

        attempts += 1

    # 최대 시도 횟수를 초과한 경우
    yield {
        "result": True,
        "error_message": "maximum number exceeded",
        "sql_script": sql_script,
    }

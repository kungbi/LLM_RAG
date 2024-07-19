import requests
from utils.chatapi import ChatAPI

from utils.token_counter import num_tokens_from_string
import streamlit as st
import json
import re

client = ChatAPI(url="http://localhost:1234/v1", model="Qwen/Qwen2-7B-Instruct-GGUF")



def generate_sql_script(query, text):
    prompt_template = f"""
    You are a MSSQL expert.

    Please help to generate a MSSQL query to answer the question. Your response should ONLY be based on the given context and follow the response guidelines and format instructions.

    ===Tables
    {text}

    ===Response Guidelines
    1. If the provided context is sufficient, please generate a valid query enclosed in string without any explanations for the question. 
    2. If the provided context is insufficient, please explain why it can't be generated.
    3. Please use the most relevant table(s).
    5. Please format the query before responding.
    6. Please always respond with a valid well-formed JSON object with the following format.
    7. Please return the JSON response without using code block formatting. The response should be directly loadable as JSON.
    8. Generate a SQL query based on the given prompt. Ensure that the SQL query includes the column names in the results. 
        For example, if the prompt is 'Get the count of students from the PERSON table,' the SQL query should be: SELECT COUNT(*) AS StudentCount FROM PERSON WHERE Discriminator='Student'. The result should include the column name 'StudentCount'.

    ===Response Format
    {{
        "query": "SELCT * FROM PERSON",
        "explanation": "The SQL query retrieves all columns and rows from the `Person` table."
    }}

    ===Question
    {query}
    """

    data = {
        "messages": [
            {"role": "system", "content": "You are a MSSQL expert."},
            {"role": "user", "content": prompt_template},
        ],
        "temperature": 0.1,
        "max_tokens": -1,
        "stream": True,  # 스트리밍 모드 활성화
    }

    try:
        response = client.send_request(str(data))
        return response

    except requests.exceptions.RequestException as e:
        print(f"Error: {e}")
        return None


def refine_sql_script(question, text, error_message):


    prompt_template = f"""
    You are a MSSQL expert.

    Please help to correct the original MSSQL query according to Error message. 
    Your response should ONLY be based on the given context and follow the response guidelines and format instructions. 
    You must not include the original input.

<<<<<<< HEAD
    ===Original Question
    {question}

    ===Error Message
    {error_message}
=======
    ===Tables
    {text}
>>>>>>> main

    ===Response Guidelines
    1. If the provided context is sufficient, please generate a valid query enclosed in string without any explanations for the question. 
    2. If the provided context is insufficient, please explain why it can't be generated.
    3. Please use the most relevant table(s).
    5. Please format the query before responding.
    6. Please always respond with a valid well-formed JSON object with the following format.
    7. Please return the JSON response without using code block formatting. The response should be directly loadable as JSON.
    8. Generate a SQL query based on the given prompt. Ensure that the SQL query includes the column names in the results.
    9. If the provided context is sufficient, please correct the original query and enclose it in string without any explanation.
    10. If the provided context is insufficient, please explain why it can't be generated.

    ===Response Format
    {{
        "refined_query": " Only corrected SQL query enclosed in string when context is sufficient.",
        "explanation": "An explanation of failing to generate the query."
    }}

    ===Original Question
    {question}

    ===Error Message
    {error_message}
    """

    data = {
        "messages": [
            {"role": "system", "content": "You are a senior data analyst."},
            {"role": "user", "content": prompt_template},
        ],
        "temperature": 0.3,
        "max_tokens": -1,
        "stream": True,  # Set to True if you need streaming
    }

    try:
        response = client.send_request(str(data))
        return response

    except requests.exceptions.RequestException as e:
        print(f"Error: {e}")
        return None


def txt2sql(question, txt, id):
    max_attempts = 4
    attempts = 0
    error_history = []
    sql_script = ""  # 여기서 sql_script를 초기화합니다

    db_api = st.session_state.db_api

    while attempts < max_attempts:
        if attempts == 0:
            response = generate_sql_script(question, txt)
        else:

            print("text2sql retry")
            response = refine_sql_script(question, txt, error_history)
        print("response:", response)

        if response is None:
            return "SQL 생성 중 오류가 발생했습니다."

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

        print(response_json)

        try:
            sql_script = response_json.get("query") or response_json.get(
                "refined_query"
            )

            if not sql_script:
                raise Exception("IDK")

            sql_result = db_api.execute(id, sql_script)
            if sql_result["result"] == False:
                raise Exception(sql_result["error"])

            return {
                "result": sql_result,
                "sql_script": sql_script,
                "attempts": attempts + 1,
            }
        except Exception as e:
            error_message = str(e)
            error_history.append(
                {
                    "attempt": attempts + 1,
                    "sql_script": sql_script,  # 이제 sql_script는 항상 정의되어 있습니다
                    "error_message": error_message,
                }
            )

            attempts += 1

    # 최대 시도 횟수를 초과한 경우
    return {
        "result": None,
        "error": f"최대 시도 횟수({max_attempts})를 초과했습니다.",
        "error_history": error_history,

        "sql_script": sql_script,  # 마지막으로 시도한 sql_script를 포함합니다
    }


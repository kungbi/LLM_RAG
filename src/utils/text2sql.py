import requests
from utils.chatapi import ChatAPI
from utils.tiktoken_api import num_tokens_from_string

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

    ===Response Format
    {{
        "query": "SELCT * FROM PERSON",
        "explanation": "The SQL query retrieves all columns and rows from the `Person` table."
    }}

    ===Question
    {query}
    """

    headers = {"Content-Type": "application/json"}

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


def refine_sql_script(original_script, error_message):

    prompt_template = f"""
    You are a MSSQL expert.

    Please help to correct the original MSSQL query according to Error message. Your response should ONLY be based on the given context and follow the response guidelines and format instructions. You must not include the original input.

    ===Original Query
    {original_script}

    ===Error Message
    {error_message}

    ===Response Guidelines
    1. If the provided context is sufficient, please correct the original query and enclose it in string without any explanation.
    2. If the provided context is insufficient, please explain why it can't be generated.
    3. Please use the most relevant table(s).
    5. Please format the query before responding.
    6. Please always respond with a valid well-formed JSON object with the following format

    ===Response Format
    {{
        "refined_query": " Only corrected SQL query enclosed in string when context is sufficient.",
        "explanation": "An explanation of failing to generate the query."
    }}

    """

    headers = {"Content-Type": "application/json"}

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

import requests
from utils.chatapi import ChatAPI
import env.llm_env as LLM_ENV
from utils import prompts


def generate_db_explain(
    schema, client=ChatAPI(url=LLM_ENV.LLM_URL, model=LLM_ENV.LLM_MODEL)
):
    prompt_template = prompts.generate_db_description(schema)

    try:
        response = client.send_request(prompt_template)
        return response

    except requests.exceptions.RequestException as e:
        return None

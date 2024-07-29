from utils import prompts
from utils.chatapi import ChatAPI
import env.llm_env as LLM_ENV

client = ChatAPI(url=LLM_ENV.LLM_URL, model=LLM_ENV.LLM_MODEL)


def generate_answer(query: str, sql_query: str, sql_result: str) -> str:
    message = prompts.generate_answer_prompt_template(query, sql_query, sql_result)
    try:
        response = client.send_request(message)
        return response

    except Exception as e:
        return None

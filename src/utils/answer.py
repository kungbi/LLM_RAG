from utils import prompts
from utils.chatapi import ChatAPI
import env.llm_env as LLM_ENV

client = ChatAPI(url=LLM_ENV.LLM_URL, model=LLM_ENV.LLM_MODEL)


def generate_answer(query: str, data: str) -> str:
    message = prompts.generate_answer_prompt_template(query, data)
    try:
        response = client.send_request(message)
        return response

    except Exception as e:
        print(f"Error: {e}")
        return None

from utils import prompts
from utils.chatapi import ChatAPI
import env.llm_env as LLM_ENV

client = ChatAPI(url=LLM_ENV.LLM_URL, model=LLM_ENV.LLM_MODEL)


def generate_answer(query: str, data: str) -> str:
    pass

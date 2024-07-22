from utils.chatapi import ChatAPI
from utils.token_limit import TokenLimit
from utils.docs_api import read_document
from utils.prompt import document_selection_prompt_template
import env.llm_env as LLM_ENV


def document_selection(question: str, document_list: list) -> list:
    document = ""
    token_count = 0
    token_limit = TokenLimit()

    for filename in document_list:
        text = read_document(filename)
        if text == None:
            continue

        tmp = ""
        tmp += filename + ": "
        tmp += text + "\n"
        tmp_token_count = token_limit.token_counter(tmp)
        if (
            not token_count + tmp_token_count
            <= LLM_ENV.LLM_DOCS_SELECTION_DCOS_MAX_TOKENS
        ):
            break

        document += tmp

    request = document_selection_prompt_template(question=question, document=document)

    chatAPI = ChatAPI(url=LLM_ENV.LLM_URL, model=LLM_ENV.LLM_MODEL)
    response = chatAPI.send_request(request)
    return response

from utils.chatapi import ChatAPI
import env.llm_env as LLM_ENV
from langchain.memory import ConversationBufferMemory

llm = ChatAPI(url=LLM_ENV.LLM_URL, model=LLM_ENV.LLM_MODEL)
memory = ConversationBufferMemory()


def generate_response(user_input):
    # 대화 기록에 사용자 입력 추가
    memory.add_message("user", user_input)

    # 이전 대화 컨텍스트를 포함하여 LLM에서 응답 생성
    context = memory.get_context()
    response = llm.generate_response(user_input, context)

    # 응답을 메모리에 저장
    memory.add_message("assistant", response)

    return response


def handle_correction(user_input, correction):
    # 대화 기록에 사용자 입력과 수정 요청 추가
    memory.add_message("user", user_input)
    memory.add_message("user", correction)

    # 수정된 응답 생성
    context = memory.get_context()
    corrected_response = llm.generate_response(correction, context)

    # 수정된 응답을 메모리에 저장
    memory.add_message("assistant", corrected_response)

    return corrected_response
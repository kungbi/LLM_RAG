from langchain.chains import LLMChain
from langchain_openai import OpenAI
from langchain.memory import ConversationBufferMemory
from langchain_core.prompts import PromptTemplate
from utils.token_limit import TokenLimit


class ChatAPI:
    def __init__(self, url, model):
        self.client = OpenAI(
            api_key="lm-studio",
            base_url=url,
            temperature=0,
        )
        self.model = model
        self.memory = ConversationBufferMemory()
        self.token_limit = TokenLimit()
        self.prompt_template = PromptTemplate(
            input_variables=["history", "input"],
            template="Chat history: {history}\nUser: {input}\nAssistant:",
        )
        self.chain = LLMChain(
            llm=self.client,
            prompt=self.prompt_template,
            memory=self.memory,
        )

    def send_request_history(self, message):
        self.memory.chat_memory.add_user_message(message)
        if not self.token_limit.is_available_full_request(message):
            return "Token limit exceeded."

        response = self.chain.predict(input=message)
        self.memory.chat_memory.add_ai_message(response)
        return response

    def send_request_history_stream(self, message):
        self.memory.chat_memory.add_user_message(message)
        if not self.token_limit.is_available_full_request(message):
            yield "Token limit exceeded."
            return

        for chunk in self.chain.predict_stream(input=message):
            self.memory.chat_memory.add_ai_message(chunk)
            yield chunk

    def send_request(self, message):
        if not self.token_limit.is_available_full_request(message):
            return "Token limit exceeded."

        response = self.chain.predict(input=message)
        return response


# Example usage:
# client = ChatAPI(
#     url="http://localhost:1234/v1",
#     model="lmstudio-community/Meta-Llama-3-8B-Instruct-BPE-fix-GGUF",
# )
# print(client.send_request("hi"))
# print(client.send_request_history("hi"))
# for chunk in client.send_request_history_stream("hi"):
#     print(chunk, end="")

from langchain.chains import LLMChain
from openai import OpenAI
from langchain.memory import ConversationBufferMemory
from langchain_core.prompts import PromptTemplate

from utils.token_limit import TokenLimit


class ChatAPI:
    def __init__(self, url, model):
        self.client = OpenAI(api_key="lm-studio", base_url=url)
        self.model = model
        self.memory = ConversationBufferMemory()
        self.token_limit = TokenLimit()
        self.prompt_template = PromptTemplate(
            input_variables=["history", "input"],
            template="Chat history: {history}\nUser: {input}\nAssistant:",
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
        print(f"message: {message}")
        if not self.token_limit.is_available_full_request(message):
            return "Token limit exceeded."
        response = self.client.chat.completions.create(
            model="TheBloke/CodeLlama-7B-Instruct-GGUF",
            messages=[
                {
                    "role": "system",
                    "content": "You are a MSSQL expert.\n Please always respond with a valid well-formed JSON object with the following format.",
                },
                {"role": "user", "content": message},
            ],
            temperature=0.0,
        )
        return response.choices[0].message.content


# Example usage:
# if __name__ == "__main__":
#     client = ChatAPI(
#         url="http://localhost:1234/v1",
#         model="TheBloke/CodeLlama-7B-Instruct-GGUF",
#     )
#     print(client.send_request("hi"))

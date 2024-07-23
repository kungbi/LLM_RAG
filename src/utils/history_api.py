from utils.chatapi import ChatAPI
import env.llm_env as LLM_ENV
from langchain.memory import ConversationBufferMemory
from langchain.schema import HumanMessage, AIMessage

class ConversationManager:
    def __init__(self):
        self.llm = ChatAPI(url=LLM_ENV.LLM_URL, model=LLM_ENV.LLM_MODEL)
        self.memory = ConversationBufferMemory(return_messages=True)

    def add_message_to_memory(self, role, content):
        """
        Add a message to the conversation memory.
        """
        if role == "user":
            self.memory.chat_memory.add_user_message(content)
        elif role == "assistant":
            self.memory.chat_memory.add_ai_message(content)

    def generate_summary(self, user_input):
        """
        Generate a summary based on the conversation history and user input.
        """
        # Add user input to memory
        self.add_message_to_memory("user", user_input)

        # Retrieve the conversation context
        context = self.memory.load_memory_variables({})["history"]

        # Construct the prompt using the context
        prompt = "Generate a summary based on the following conversation history:\n"
        for message in context:
            if isinstance(message, HumanMessage):
                prompt += f"Human: {message.content}\n"
            elif isinstance(message, AIMessage):
                prompt += f"AI: {message.content}\n"
        prompt += f"Human: {user_input}\nAI:"

        # Generate the response using the LLM
        response = self.llm.send_request(prompt)

        # Add the response to memory
        self.add_message_to_memory("assistant", response)
        print("summary:",response)

        return response

    def handle_correction(self, user_input, correction):
        """
        Handle a correction to a previous response.
        """
        # Add user input and correction to memory
        self.add_message_to_memory("user", user_input)
        self.add_message_to_memory("user", correction)

        # Generate corrected response
        context = self.memory.load_memory_variables({})["history"]
        prompt = "Based on the following conversation, provide a corrected response:\n"
        for message in context:
            if isinstance(message, HumanMessage):
                prompt += f"Human: {message.content}\n"
            elif isinstance(message, AIMessage):
                prompt += f"AI: {message.content}\n"
        prompt += f"Human: {correction}\nAI:"

        corrected_response = self.llm.send_request(prompt)

        # Add the corrected response to memory
        self.add_message_to_memory("assistant", corrected_response)

        return corrected_response
from utils.chatapi import ChatAPI
import env.llm_env as LLM_ENV
from langchain.memory import ConversationBufferMemory
from langchain.schema import HumanMessage, AIMessage
import json


class ConversationManager:
    def __init__(self):
        self.llm = ChatAPI(url=LLM_ENV.LLM_URL, model=LLM_ENV.LLM_MODEL)
        self.memory = ConversationBufferMemory(return_messages=True)
        self.turn_counter = 0

    def add_user_message_to_memory(self, content):
        """
        Add a user message to the conversation memory with turn numbering.
        """
        self.turn_counter += 1
        turn_header = f"===Turn {self.turn_counter}:\n\n"
        full_content = f"{turn_header}Human: {content}\n"
        self.memory.chat_memory.add_user_message(full_content)

    def add_ai_response_to_memory(self, combined_response_str):
        """
        Add an AI response to the conversation memory with detailed explanations.
        """
        try:
            responses = json.loads(combined_response_str)
            full_content = ""
            for response in responses:
                full_content += f"AI Response {response.get('num', '')}:\n"

                if response.get('query') is None:
                    full_content += "Status: Failed to generate SQL Script\n"
                elif not response.get('result'):
                    full_content += "Status: Error in SQL Script generation\n"
                else:
                    full_content += "Status: SQL Script generated successfully\n"

                if response.get('query'):
                    full_content += f"Generated SQL Script: {response.get('query')}\n"

                if not response.get('sql'):
                    full_content += "SQL Execution: Failed\n"
                else:
                    full_content += "SQL Execution: Successful\n"

                if response.get('sql_result'):
                    full_content += f"SQL Execution Result:\n{response.get('sql_result')}\n"

                if response.get('message'):
                    full_content += f"Error Message: {response.get('message')}\n"

                if response.get('answer'):
                    full_content += f"Final Answer: {response.get('answer')}\n"

                full_content += "\n"

            self.memory.chat_memory.add_ai_message(full_content.strip())
        except json.JSONDecodeError:
            print("Error: Invalid JSON string")

    def generate_summary(self, user_input):
        """
        Generate a summary based on the conversation history and user input.
        """
        #
        # Retrieve the conversation context
        context = self.memory.load_memory_variables({})["history"]

        # Construct the prompt using the context
        prompt = """
        Your job is to produce a final summary.
        Write a concise summary of the following:\n
        """
        for message in context:
            if isinstance(message, HumanMessage):
                prompt += f"Human: {message.content}\n"
            elif isinstance(message, AIMessage):
                prompt += f"AI: {message.content}\n"
        prompt += f"Human: {user_input}\nAI:"

        # Generate the response using the LLM
        response = self.llm.send_request(prompt)

        # Add the response to memory
        # print("summary:",response)


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
        prompt = """
        Based on the following conversation, provide a corrected response:\n
        """
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

    def print_conversation_history(self):
        """
        Print the entire conversation history.
        """
        messages = self.memory.chat_memory.messages
        for message in messages:
            if isinstance(message, HumanMessage):
                print(f"Human: {message.content}")
            elif isinstance(message, AIMessage):
                print(f"AI: {message.content}")

    def get_full_conversation_history(self):
        """
        Return entire history
        """
        messages = self.memory.chat_memory.messages
        conversation_history = ""
        for message in messages:
            if isinstance(message, HumanMessage):
                conversation_history += f"Human: {message.content}\n"
            elif isinstance(message, AIMessage):
                conversation_history += f"AI: {message.content}\n"
        return conversation_history
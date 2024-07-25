import sys, os

sys.path.append(os.path.join(os.path.dirname(__file__), ".."))

from utils.chatapi import ChatAPI
from utils import prompts
import env.llm_env as LLM_ENV
from langchain.memory import ConversationBufferMemory
from langchain.schema import HumanMessage, AIMessage
import json


class ConversationManager:

    def __init__(self, summary_ratio=0.5):
        self.llm = ChatAPI(url=LLM_ENV.LLM_URL, model=LLM_ENV.LLM_MODEL)
        self.summary = ""
        self.memory = ConversationBufferMemory(return_messages=True)
        self.turn_counter = 0
        self.summary_ratio = summary_ratio

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

                if response.get("query") is None:
                    full_content += "Status: Failed to generate SQL Script\n"
                elif not response.get("result"):
                    full_content += "Status: Error in SQL Script generation\n"
                else:
                    full_content += "Status: SQL Script generated successfully\n"

                if response.get("query"):
                    full_content += f"Generated SQL Script: {response.get('query')}\n"

                if not response.get("sql"):
                    full_content += "SQL Execution: Failed\n"
                else:
                    full_content += "SQL Execution: Successful\n"

                if response.get("sql_result"):
                    full_content += (
                        f"SQL Execution Result:\n{response.get('sql_result')}\n"
                    )

                if response.get("message"):
                    full_content += f"Error Message: {response.get('message')}\n"

                if response.get("answer"):
                    full_content += f"Final Answer: {response.get('answer')}\n"

                full_content += "\n"

            self.memory.chat_memory.add_ai_message(full_content.strip())
        except json.JSONDecodeError:
            print("Error: Invalid JSON string")

    def summarize_and_update_buffer(self):
        summary, remaining = self._generate_summary()
        self.summary = summary
        self.memory.clear()
        for messages in remaining:
            for data in messages:
                if isinstance(data, HumanMessage):
                    self.memory.chat_memory.add_user_message(data.content)
                else:
                    self.memory.chat_memory.add_ai_message(data.content)

    def _generate_summary(self):
        context = self.memory.load_memory_variables({})["history"]
        paired_context = []
        tmp = []
        for data in context:
            if isinstance(data, HumanMessage):
                if tmp:
                    paired_context.append(tmp)
                    tmp = []
                tmp.append(data)
            else:
                tmp.append(data)

        pair_len = len(paired_context)
        summary_length = int(pair_len * self.summary_ratio)

        summary_sentences = paired_context[:summary_length]
        remaining_sentences = paired_context[summary_length:]

        history_data_str = ""
        for messages in summary_sentences:
            for data in messages:
                if isinstance(data, HumanMessage):
                    history_data_str += f"Human: {data.content}\n"
                elif isinstance(data, AIMessage):
                    history_data_str += f"AI: {data.content}\n"

        prompt = prompts.generate_data_summary_prompt(history_data_str)
        response = self.llm.send_request(prompt)

        if self.summary != "":
            prompt = prompts.generate_combined_summary_prompt(response, self.summary)
            final_summary = self.llm.send_request(prompt)

        return response if self.summary == "" else final_summary, remaining_sentences

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
        if self.summary != "":
            messages = f"Summary: {self.summary}"

        for message in messages:
            if isinstance(message, HumanMessage):
                conversation_history += f"Human: {message.content}\n"
            elif isinstance(message, AIMessage):
                conversation_history += f"AI: {message.content}\n"
        return conversation_history


if __name__ == "__main__":
    conversation_manager = ConversationManager()
    for i in range(5):
        conversation_manager.add_user_message_to_memory(f"{i} how many studnet?")
        for j in range(2 if i % 2 == 0 else 1):
            conversation_manager.add_ai_response_to_memory(
                json.dumps(
                    [
                        {
                            "num": 1,
                            "query": "sdafasdf",
                            "sql": "asdfasdf",
                            "sql_result": "asdfasdf",
                        }
                    ]
                )
            )
    conversation_manager.summary = "The conversation involves a human asking about the number of instructors, and it was 100"
    conversation_manager.summarize_and_update_buffer()
    print(conversation_manager.summary)
    print()
    print(conversation_manager.memory.load_memory_variables({})["history"])

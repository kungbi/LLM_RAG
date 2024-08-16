from typing import List
import env.llm_env as LLM_ENV
from transformers import Qwen2Tokenizer
from transformers import AutoTokenizer
from collections import deque


class TokenLimit:
    def __init__(self) -> None:
        if "Qwen" in LLM_ENV.LLM_MODEL:
            self.tokenizer: function = Qwen2Tokenizer.from_pretrained(
                "Qwen/Qwen-tokenizer"
            )
        else:
            self.tokenizer: function = Qwen2Tokenizer.from_pretrained(
                "Qwen/Qwen-tokenizer"
            )

    def token_counter(self, text: str) -> int:
        return len(self.tokenizer(text)["input_ids"])

    def split_document_by_tokens(
        self, text: str, max_tokens: int = LLM_ENV.LLM_TEXT2SQL_DOCS_MAX_TOKENS
    ) -> str:
        encoding = self.tokenizer(text)["input_ids"]
        return self.tokenizer.decode(encoding[:max_tokens])

    def is_available_docs_selection(self, docs: str, prompt: str) -> bool:
        docs_token_len = self.token_counter(docs)
        if not docs_token_len <= LLM_ENV.LLM_DOCS_SELECTION_DCOS_MAX_TOKENS:
            return False

        prompt_token_len = self.token_counter(prompt)
        if not prompt_token_len <= LLM_ENV.LLM_DOCS_SELECTION_PROMPT_MAX_TOKENS:
            return False
        return True

    def is_available_history(self, history: str) -> bool:
        history_token_len = self.token_counter(history)
        if not history_token_len <= LLM_ENV.LLM_TEXT2SQL_HISTORY_MAX_TOKENS:
            return False
        return True

    def is_available_text2sql(self, docs: str, prompt: str, history: str) -> bool:
        docs_token_len = self.token_counter(docs)
        if not docs_token_len <= LLM_ENV.LLM_TEXT2SQL_DOCS_MAX_TOKENS:
            return False

        prompt_token_len = self.token_counter(prompt)
        if not prompt_token_len <= LLM_ENV.LLM_TEXT2SQL_PROMPT_MAX_TOKENS:
            return False

        history_token_len = self.token_counter(history)
        if not history_token_len <= LLM_ENV.LLM_TEXT2SQL_HISTORY_MAX_TOKENS:
            return False

        return True

    def is_available_full_request(self, message: str) -> bool:
        message_token_len = self.token_counter(message)
        if not message_token_len <= LLM_ENV.LLM_MAX_TOKENS:
            return False
        return True

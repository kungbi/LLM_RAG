import tiktoken
from transformers import Qwen2Tokenizer


def num_tokens_from_string(string: str, encoding_name: str = "r50k_base") -> int:
    """Returns the number of tokens in a text string."""
    encoding = tiktoken.get_encoding(encoding_name)
    num_tokens = len(encoding.encode(string))
    return num_tokens


def num_tokens_from_string_qwen(string: str):
    tokenizer = Qwen2Tokenizer.from_pretrained("Qwen/Qwen-tokenizer")
    encoding = tokenizer("Hello world")["input_ids"]
    return len(encoding)

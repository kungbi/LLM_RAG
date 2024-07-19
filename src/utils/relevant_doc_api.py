from utils.token_counter import num_tokens_from_string
from utils.token_counter import num_tokens_from_string_qwen
import os


def merge_text_files(file_list=[], token_limit=5000):
    text = ""
    token_count = 0

    for filename in file_list:
        tmp = ""
        tmp += f"filename: {filename}\n"

        file_path = os.path.join("data", filename)
        if not os.path.exists(file_path):
            continue

        with open(file_path, "r") as f:
            tmp += f.read() + "\n"
        count = num_tokens_from_string_qwen(tmp)
        if token_limit < token_count + count:
            break
        text += tmp
        token_count += count

    return text, token_count

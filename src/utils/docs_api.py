import os


def read_document(filename):
    file_path = os.path.join("data", filename)
    if not os.path.exists(file_path):
        return None

    with open(file_path, "r") as f:
        text = f.read() + "\n"

    return text


def merge_text_files(file_list=[]):
    text = ""
    for filename in file_list:
        content = read_document(filename)
        if content == None:
            continue

        text += f"filename: {filename}\n"
        text += content

    return text

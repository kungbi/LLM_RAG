import os, shutil
import sys
from utils.db_api import DB_Configuration
from utils import opensearch_api
from utils.opensearch_api import SearchAPI
from utils import doc_extract_core


class DocExtract:
    INDEX_NAME: str = "database_schema"

    def __init__(self, db_info: DB_Configuration, tab) -> None:
        self.db_info = db_info
        self.opensearch: SearchAPI = opensearch_api.connect()
        self.opensearch.create_index(self.INDEX_NAME)
        self.current_tab = tab
        self.base_dir = f"./conv/Chat_{tab}/schema"  # 변경된 기본 경로

    def reset(self):
        if os.path.isdir(self.base_dir):
            shutil.rmtree(self.base_dir)
        os.makedirs( self.base_dir)
        self.opensearch.delete_index(self.INDEX_NAME)
        self.opensearch.create_index(self.INDEX_NAME)


    def extract(self, tab):
        doc_extract_core.start(self.db_info,tab)
        self.upload_opensearch()

    def upload_opensearch(self):
        filename_list = get_schema_list(self.base_dir)
        for filename in filename_list:
            file_path = os.path.join(self.base_dir, filename)
            with open(file_path, "r") as file:
                text = file.read()
                self.opensearch.index_document_chunk(self.INDEX_NAME, filename, text)

def get_schema_list(base_dir: str):
    result = []
    if not os.path.isdir(base_dir):
        return result

    for filename in os.listdir(base_dir):
        if filename.endswith(".txt"):
            result.append(filename)
    return sorted(result)


def start_extract(db_info: DB_Configuration, tab):
    doc_extract = DocExtract(db_info, tab)
    doc_extract.reset()
    doc_extract.extract(tab)


if __name__ == "__main__":
    print(get_schema_list())
    start_extract()
    print(get_schema_list())

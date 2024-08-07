import os, shutil
import sys
from utils.db_api import DB_Configuration
from utils import opensearch_api
from utils.opensearch_api import SearchAPI
from utils import doc_extract_core


class DocExtract:
    INDEX_NAME: str = "database_schema"

    def __init__(self, db_info: DB_Configuration) -> None:
        self.db_info = db_info
        self.opensearch: SearchAPI = opensearch_api.connect()
        self.opensearch.create_index(self.INDEX_NAME)

    def reset(self):
        if os.path.isdir("./schema"):
            shutil.rmtree("schema")
        os.makedirs("schema")
        self.opensearch.delete_index(self.INDEX_NAME)
        self.opensearch.create_index(self.INDEX_NAME)

    def extract(self):
        doc_extract_core.start(self.db_info)
        self.upload_opensearch()

    def upload_opensearch(self):
        filename_list = get_schema_list()
        for filename in filename_list:
            script_dir = os.path.dirname(os.path.abspath(__file__))
            output_dir = os.path.join(script_dir, "../../schema")
            file_path = os.path.join(output_dir, filename)
            with open(file_path, "r") as file:
                text = file.read()
                self.opensearch.index_document_chunk(self.INDEX_NAME, filename, text)


def get_schema_list():
    result = []
    if not os.path.isdir("./schema"):
        return result

    for filename in os.listdir("./schema"):
        if filename.endswith(".txt"):
            result.append(filename)
    return sorted(result)


def start_extract(db_info: DB_Configuration):
    doc_extract = DocExtract(db_info)
    doc_extract.reset()
    doc_extract.extract()


if __name__ == "__main__":
    print(get_schema_list())
    start_extract()
    print(get_schema_list())

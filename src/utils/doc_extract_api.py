import os, shutil
import sys

# sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from utils import opensearch_api
from utils.opensearch_api import SearchAPI
from utils import doc_extract_core


class DocExtract:
    INDEX_NAME: str = "database_schema"

    def __init__(self) -> None:
        self.opensearch: SearchAPI = opensearch_api.connect()
        self.opensearch.create_index(self.INDEX_NAME)

    def reset(self):
        if os.path.isdir("./schema"):
            shutil.rmtree("schema")
        os.makedirs("schema")
        self.opensearch.delete_index(self.INDEX_NAME)
        self.opensearch.create_index(self.INDEX_NAME)

    def extract(self):
        doc_extract_core.start()

    def upload_opensearch(self):
        pass


def get_schema_list():
    result = []
    if not os.path.isdir("./schema"):
        return result

    for filename in os.listdir("./schema"):
        if filename.endswith(".txt"):
            result.append(filename)
    return sorted(result)


def start_extract():
    doc_extract = DocExtract()
    doc_extract.reset()
    doc_extract.extract()


if __name__ == "__main__":
    print(get_schema_list())
    start_extract()
    print(get_schema_list())

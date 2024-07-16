from opensearchpy import OpenSearch
from sentence_transformers import SentenceTransformer


class SearchAPI:
    def __init__(self, client, model):
        self.client = client
        self.model = model

    def create_index(self, index_name):
        if not self.client.indices.exists(index=index_name):
            index_body = {
                "settings": {"index": {"knn": True}},
                "mappings": {
                    "properties": {
                        "filename": {"type": "keyword"},
                        "chunk": {"type": "text"},
                        "embedding": {"type": "knn_vector", "dimension": 384},
                    }
                },
            }
            self.client.indices.create(index=index_name, body=index_body)

    def delete_index(self, index_name):
        try:
            response = self.client.indices.delete(index=index_name)
            return response
        except Exception as e:
            print(e)
            return None

    def encode(self, text):
        return self.model.encode(text)

    def index_document(self, index_name, doc_id, document):
        self.client.index(index=index_name, id=doc_id, body=document)

    def search(self, index_name, search_body):
        return self.client.search(index=index_name, body=search_body)

    def get_client(self):
        return self.client


def get_client():
    ca_certs_path = "./src/utils/root-ca.pem"
    client = OpenSearch(
        hosts=[{"host": "localhost", "port": 9200}],
        http_auth=("admin", "StrongPassword123!"),
        http_compress=True,
        use_ssl=True,
        verify_certs=True,
        ssl_assert_hostname=False,
        ssl_show_warn=False,
        ca_certs=ca_certs_path,
    )
    model = SentenceTransformer("sentence-transformers/all-MiniLM-L6-v2")
    return SearchAPI(client, model)

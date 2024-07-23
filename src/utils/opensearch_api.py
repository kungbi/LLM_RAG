from opensearchpy import OpenSearch
from sentence_transformers import SentenceTransformer
import env.opensearch_env as opensearch_env
import utils.opensearch_query as opensearch_query
from langchain_text_splitters.character import CharacterTextSplitter


class SearchAPI:
    def __init__(self, client, model):
        self.client = client
        self.model = model

    def create_index(self, index_name):
        if not self.client.indices.exists(index=index_name):
            index_body = opensearch_query.build_create_query()
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

    def index_document_chunk(self, index_name, filename, text):
        chunks = chunk_sentences(text)
        for i, chunk in enumerate(chunks):
            embedding = self.encode(chunk)
            action = opensearch_query.build_index_query(filename, chunk, embedding)
            self.index_document(index_name, f"{filename}_{i}", action)

    def search(self, index_name, search_body):
        return self.client.search(index=index_name, body=search_body)

    def get_client(self):
        return self.client

    def create_index2(self, index_name):
        if not self.client.indices.exists(index=index_name):
            index_body = opensearch_query.build_create_query2()
            self.client.indices.create(index=index_name, body=index_body)

    def index_tables(self, text):
        embedding = self.encode(text).tolist()
        body = opensearch_query.build_index_query2(text, embedding)
        self.client.index(index="application_tables", body=body)

    def index_column(self, text):
        embedding = self.encode(text).tolist()
        body = opensearch_query.build_index_query2(text, embedding)
        self.client.index(index="application_columns", body=body)

    def search_tables(self, query: str):
        embedding = self.encode(query).tolist()
        body = opensearch_query.build_search_query2(embedding, 5)
        return self.client.search(index="application_tables", body=body)

    def search_columns(self, query):
        embedding = self.encode(query).tolist()
        body = opensearch_query.build_search_query2(embedding, 10)
        return self.client.search(index="application_columns", body=body)


# 텍스트를 청크로 분할하는 함수
def chunk_sentences(text, chunk_size=300, chunk_overlap=100):
    text_splitter = CharacterTextSplitter(
        chunk_size=chunk_size, chunk_overlap=chunk_overlap
    )
    return text_splitter.split_text(text)


def connect():
    client = OpenSearch(
        hosts=[
            {
                "host": opensearch_env.OPENSEARCH_HOST,
                "port": opensearch_env.OPENSEARCH_PORT,
            }
        ],
        http_auth=(opensearch_env.OPENSEARCH_USR, opensearch_env.OPENSEARCH_PWD),
        http_compress=True,
        use_ssl=True,
        verify_certs=True,
        ssl_assert_hostname=False,
        ssl_show_warn=False,
        ca_certs=opensearch_env.OPENSEARCH_CA_CERT_PATH,
    )
    model = SentenceTransformer("sentence-transformers/all-MiniLM-L6-v2")
    return SearchAPI(client, model)

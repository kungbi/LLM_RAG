import streamlit as st
from utils.chatapi import ChatAPI
import utils.opensearch_api as opensearch_api
from utils.search_query import build_search_query
from app import INDEX_NAME
from utils.relevant_doc_api import merge_text_files


def main():
    st.title("💬 Llama3 7B")
    st.caption("🚀 A Streamlit chatbot powered by Llama3 7B")

    # st.session_state를 사용하여 history 상태 유지
    if "history" not in st.session_state:
        st.session_state.history = []

    if "client" not in st.session_state:
        st.session_state.client = ChatAPI(
            url="http://localhost:1234/v1",
            model="lmstudio-community/Meta-Llama-3-8B-Instruct-BPE-fix-GGUF",
        )
    client = st.session_state.client

    if "messages" not in st.session_state:
        st.session_state.messages = [
            {"role": "assistant", "content": "How can I help you?"}
        ]

    if "opensearch" not in st.session_state:
        st.session_state.opensearch = opensearch_api.connect()
    opensearch = st.session_state.opensearch

    for msg in st.session_state.messages:
        st.chat_message(msg["role"]).write(msg["content"])

    if prompt := st.chat_input():
        # opeansearch
        query = build_search_query(query_embedding=opensearch.encode(prompt))
        response = opensearch.search(INDEX_NAME, query)
        response = (
            response.get("aggregations", {})
            .get("group_by_filename", {})
            .get("buckets", [])
        )
        relev_docs = [data["key"] for data in response]
        text = merge_text_files(relev_docs, token_limit=4000)

        # st.session_state.messages.append({"role": "user", "content": prompt})
        # st.chat_message("user").write(prompt)
        # with st.chat_message("assistant"):
        #     response = client.send_request_history_stream(prompt)
        #     placeholder = st.empty()
        #     full_response = ""
        #     for item in response:
        #         full_response += item
        #         placeholder.markdown(full_response)
        #     placeholder.markdown(full_response)
        # message = {"role": "assistant", "content": full_response}
        # st.session_state.messages.append(message)


main()

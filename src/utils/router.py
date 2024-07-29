from semantic_router import Route

sql_request = Route(
    name="SQLRequestRouter",
    utterances=[
        "SELECT * FROM users",
        "Can you write a SQL query to get all users?",
        "I need an INSERT statement for the customers table",
        "Update the product price in the database",
        "Delete all orders older than 30 days",
        "Show me the schema for the users table",
        "what is the number of student?"
    ],
)

general_conversation = Route(
    name="GeneralConversationRouter",
    utterances=[
        "Hi there!",
        "How are you doing today?",
        "What can this application do?",
        "Tell me a joke",
        "What's the weather like?",
        "Who created you?",
    ],
)

follow_up = Route(
    name="FollowUpRouter",
    utterances=[
        "Can you explain that last query?",
        "What does this result mean?",
        "Show me more details about the first row",
        "Why did we get these results?",
        "How can I modify this query to include the user's age?",
        "What if I want to sort by date instead?",
    ],
)

error_correction = Route(
    name="ErrorCorrectionRouter",
    utterances=[
        "That's not correct, the table name should be 'employees'",
        "There's an error in the WHERE clause",
        "You forgot to include the JOIN condition",
        "The column name is wrong, it should be 'first_name'",
        "This query is giving me an error, can you fix it?",
        "The data types don't match in the comparison",
    ],
)

meta_query = Route(
    name="MetaQueryRouter",
    utterances=[
        "What are the capabilities of this system?",
        "Can you explain how the database is structured?",
        "What types of SQL queries can you handle?",
        "How do you ensure data privacy?",
        "What's the difference between this and a regular SQL client?",
        "Are there any limitations to the queries I can run?",
    ],
)

routes = [sql_request, general_conversation, follow_up, error_correction, meta_query]





from semantic_router.encoders import HuggingFaceEncoder

encoder = HuggingFaceEncoder()

from semantic_router import RouteLayer

from llama_cpp import Llama
from semantic_router.llms.llamacpp import LlamaCppLLM

enable_gpu = True  # offload LLM layers to the GPU (must fit in memory)

import sys
import logging
from contextlib import contextmanager

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

@contextmanager
def llama_context():
    logger.info("Initializing Llama model...")
    _llm = Llama(
        model_path="/Users/sean/.cache/lm-studio/models/lmstudio-community/Meta-Llama-3-8B-Instruct-GGUF/Meta-Llama-3-8B-Instruct-IQ3_M.gguf",
        n_gpu_layers=-1 if enable_gpu else 0,
        n_ctx=2048,
    )
    _llm.verbose = False
    llm = LlamaCppLLM(name="Meta-Llama-3-8B-Instruct-GGUF", llm=_llm, max_tokens=None)
    logger.info("Llama model initialized")
    try:
        yield llm
    finally:
        logger.info("Cleaning up Llama model...")
        del _llm
        del llm
        logger.info("Cleanup complete")

def main():
    logger.info("Starting main execution")
    with llama_context() as llm:
        logger.info("Creating RouteLayer")
        rl = RouteLayer(encoder=encoder, routes=routes, llm=llm)
        logger.info("Sending query to RouteLayer")
        query = "what is the number of instructor?"
        logger.info(f"Query: {query}")
        out = rl(query)
        logger.info(f"Received output: {out}")
        print("Output:", out)
        sys.stdout.flush()
    logger.info("Main execution completed")

if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        logger.exception("An error occurred during execution")
    finally:
        print("Script execution completed")
        sys.stdout.flush()


# 라우터 사용 예시 (실제 구현은 semantic_router 라이브러리의 기능에 따라 달라질 수 있습니다)
# from semantic_router import Router
# router = Router(routes)
#
# def process_query(query: str):
#     result = router(query)
#     print(f"Query: {query}")
#     print(f"Routed to: {result.name}")
#
# # 테스트
# test_queries = [
#     "SELECT * FROM users WHERE age > 30",
#     "Hi, how are you doing today?",
#     "Can you explain the last query result?",
#     "That's wrong, the table name should be 'customers', not 'users'",
#     "What are the capabilities of this system?",
#     "Update the user's email address",
# ]
#
# for query in test_queries:
#     process_query(query)
#     print()
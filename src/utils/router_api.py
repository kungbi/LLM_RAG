from semantic_router import Route
from semantic_router.encoders import HuggingFaceEncoder
from semantic_router import RouteLayer
from llama_cpp import Llama
from semantic_router.llms.llamacpp import LlamaCppLLM
import sys
import logging
from contextlib import contextmanager


sql_request = Route(
    name="SQLRequestRouter",
    utterances=[
        "What are the course of Engineering",
        "What is the number of the student?",
        "How many instructor?",
        "What is the total budget for all departments combined?",
        "What is Gytis Barzdukas's average grade?",
        "Please list the name of each instructor and the location of their office assignments.",
        "What is the budget for the Mathematics department?",
        "Which students were enrolled after January 1, 2005?",
        "What is the average grade of students in each course? (join, group by, aggregation)",
        "Which departments have more than two courses, and what is the total number of courses in those departments? (rank function)",
        "For each course, rank the students based on their grades. Display only the top 3 students for each course.",
        "What are the capabilities of this system?",
        "Can you explain how the database is structured?",
        "What types of SQL queries can you handle?",
        "How do you ensure data privacy?",
        "What's the difference between this and a regular SQL client?",
        "Are there any limitations to the queries I can run?",
        "what model you are?"
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


routes = [sql_request, general_conversation]



encoder = HuggingFaceEncoder()
enable_gpu = True  # offload LLM layers to the GPU (must fit in memory)


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

def semantic_layer(query: str):
    logger.info("Starting main execution")
    with llama_context() as llm:
        logger.info("Creating RouteLayer")
        rl = RouteLayer(encoder=encoder, routes=routes, llm=llm)
        logger.info("Sending query to RouteLayer")
        logger.info(f"Query: {query}")
        out = rl(query)
        logger.info(f"Received output: {out}")
        print("Output:", out)
        sys.stdout.flush()
    logger.info("Main execution completed")

    return out




## Usage

# route = semanatic_layer(query)
#     if route.name == "sql_request":
#         response = text2sql()
#     elif route.name == "brand_protection":
#         response = sent_request_llm()
#     else:
#         pass
#     return query



# def main(query: str):
#     route = semantic_layer(query)
#     if route.name == "sql_request":
#         query += f" (SYSTEM NOTE: {route.name})"
#     elif route.name == "brand_protection":
#         query += f" (SYSTEM NOTE: {route.name})"
#     else:
#         pass
#     return query
#
# if __name__ == "__main__":
#     try:
#         main(input())
#     except Exception as e:
#         logger.exception("An error occurred during execution")
#     finally:
#         print("Script execution completed")
#         sys.stdout.flush()






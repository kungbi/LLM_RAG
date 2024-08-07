# Text2SQL
✨Run Text2SQL in your local machine and connect to DB!✨


## Getting Started

### Prerequisites 

- LM Studio
  - Qwen/Qwen2-7B-Instruct-GGUF/qwen2-7b-instruct-q4_0.gguf
  - lmstudio-community/Meta-Llama-3-8B-Instruct-GGUF/Meta-Llama-3-8B-Instruct-IQ3_M.gguf
  -  nomic-ai/nomic-embed-text-v1.5-GGUF/nomic-embed-text-v1.5.Q8_0.gguf
- MS SQL Server (ODBC Driver 18 for SQL Server or ODBC Driver 17 for SQL Server)
- OpenSearch Server

### Installation
```
$ python3 -m venv .env
$ source .env/bin/activate
$ pip install -r requirements.txt
```

### Add LLM Path for Semantic Router
```
#Open the file `/env/llama_env.py`
#add path to LMStudio local llama model

LLAMA_MODEL_PATH = "/path/to/your/model/Meta-Llama-3-8B-Instruct-IQ3_M.gguf"
```


### Start Application

```
$ streamlit run src/app.py
```

## About The Project
**Text2SQL** is a LLM domain for generating output based on DB schema and information from user's query.

Below is the the lifecycle of the application:

- **Connect to DB**:
- **Connect to local LLM**: 
- **Connect to OpenSearch and Index DB Schema**:
- **Query Input**: 


### Flowchart
![Text_to_SQL_Flowchart (1)](https://github.com/user-attachments/assets/23fc49c0-538e-4331-87d0-cb4417226493)

### Built with
- ![Python](https://img.shields.io/badge/Python-3776AB?style=for-the-badge&logo=python&logoColor=white)
- ![OpenSearch](https://img.shields.io/badge/OpenSearch-005EB8?style=for-the-badge&logo=opensearch&logoColor=white)
- ![LangChain](https://img.shields.io/badge/LangChain-000000?style=for-the-badge&logo=langchain&logoColor=white)
- ![Streamlit](https://img.shields.io/badge/Streamlit-FF4B4B?style=for-the-badge&logo=streamlit&logoColor=white)
- ![Docker](https://img.shields.io/badge/Docker-2496ED?style=for-the-badge&logo=docker&logoColor=white)
- ![LM Studio](https://img.shields.io/badge/LM%20Studio-FF6F00?style=for-the-badge&logo=lm-studio&logoColor=white)
- ![MSSQL](https://img.shields.io/badge/MSSQL-CC2927?style=for-the-badge&logo=microsoft-sql-server&logoColor=white)




## Acknowledgments 


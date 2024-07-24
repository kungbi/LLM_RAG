def generate_sql_script(query, text, context):
    prompt_template = f"""
    You are a MSSQL expert.

    Please help to generate a MSSQL query to answer the question. Your response should ONLY be based on the given context and follow the response guidelines and format instructions.

    ===Tables
    {text}
    
    ===Context
    {context}
    

    ===Response Guidelines
    1. If the provided context is sufficient, please generate a valid query enclosed in string without any explanations for the question. 
    2. If the provided context is insufficient, please explain why it can't be generated.
    3. Please use the most relevant table(s).
    5. Please format the query before responding.
    6. Please always respond with a valid well-formed JSON object with the following format.
    7. Please return the JSON response without using code block formatting. The response should be directly loadable as JSON.
    8. Generate a SQL query based on the given prompt. Ensure that the SQL query includes the column names in the results. 
        For example, if the prompt is 'Get the count of students from the PERSON table,' the SQL query should be: SELECT COUNT(*) AS StudentCount FROM PERSON WHERE Discriminator='Student'. The result should include the column name 'StudentCount'.
    9. NOTE: Use SQL 'AS' statement to assign a new name temporarily to a table column or even a table wherever needed. 

    ===Response Format
    {{
        "query": "SELCT * FROM PERSON",
        "explanation": "The SQL query retrieves all columns and rows from the `Person` table."
    }}

    ===Question
    {query}
    """
    return prompt_template


def generate_refine_sql_script(query, text, formatted_error_history, context):
    prompt_template = f"""
    You are a MSSQL expert.

    Please help to correct the original MSSQL query according to Error message. 
    Your response should ONLY be based on the given context and follow the response guidelines and format instructions. 
    You must not include the original input.


    ===Tables
    {text}
    
    
    {formatted_error_history}

    ===Response Guidelines
    1. If the provided context is sufficient, please generate a valid query enclosed in string without any explanations for the question. 
    2. If the provided context is insufficient, please explain why it can't be generated.
    3. Please use the most relevant table(s).
    5. Please format the query before responding.
    6. Please always respond with a valid well-formed JSON object with the following format.
    7. Please return the JSON response without using code block formatting. The response should be directly loadable as JSON.
    8. Generate a SQL query based on the given prompt. Ensure that the SQL query includes the column names in the results.
    9. If the provided context is sufficient, please correct the original query and enclose it in string without any explanation.
    10. If the provided context is insufficient, please explain why it can't be generated.
    11. NOTE: Use SQL 'AS' statement to assign a new name temporarily to a table column or even a table wherever needed. 

    ===Response Format
    {{
        "refined_query": " Only corrected SQL query enclosed in string when context is sufficient.",
        "explanation": "An explanation of failing to generate the query."
    }}

    ===Original Question
    {query}

    """
    return prompt_template


def document_selection_prompt_template(question: str, document: str):
    template = f"""
    You are provided with a specific question and several files along with their contents. 
    Your task is to analyze the contents of each file and determine their importance in answering the question. 
    Reorder the file names based on their relevance to the question and output the result in JSON format, with the most important file at the top and the least important file at the bottom.

    Here is an example:

    Question: {question}

    Files and Contents:
    {document}
    
    Output the reordered file names in JSON format, with the most relevant file first and the least relevant file last. 


    Example JSON output:
    {{
        "reordered_files": [
            "department.txt",
            "course_instructor.txt",
            "office_assignment.txt",
            "course.txt"
        ]
    }}
    """
    return template


def generate_answer_prompt_template(question: str, sql_query: str, sql_result: str):
    template = f"""
    You are an expert business assistant.

    Please generate a detailed and accurate answer to the given question using the provided SQL query and its result. Your response should ONLY be based on the given context and follow the response guidelines and format instructions.

    ===SQL Query
    {sql_query}

    ===SQL Result
    {sql_result}

    ===Response Guidelines
    1. If the provided context is sufficient, please generate a direct and informative answer to the question in complete sentences.
    2. If the provided context is insufficient, please explain why the question can't be answered.
    3. Please use the most relevant information from the provided SQL result.
    4. Please format the answer clearly and concisely.
    5. Always respond with a valid well-formed JSON object with the following format.
    6. Please return the JSON response without using code block formatting. The response should be directly loadable as JSON.
    7. Ensure that the answer directly addresses the question and includes all necessary details in a professional manner.

    ===Response Format
    {{
        "answer": "Your detailed and accurate answer in complete sentences."
    }}

    ===Question
    {question}
    """
    return template

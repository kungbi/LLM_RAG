def generate_sql_script(query, text, context):
    prompt_template = f"""
    You are a MSSQL expert.

    Generate a MSSQL query to answer the question. 
    Your response should ONLY be based on the given context and follow the response guidelines and format instructions.

    ===Tables
    {text}
    
    ===Previous Conversation
    {context}

    ===Response Guidelines
    1. If the provided context is sufficient, generate a valid query enclosed in a string without any explanations for the question.
    2. If the provided context is insufficient, explain why it can't be generated on explanation section politely.
    3. Use the most relevant table(s).
    4. Only use the provided table names and column names; do not use any other names.
    5. Format the query before responding.
    6. Ensure the SQL query is executable without any modifications.
    7. Always respond with a valid well-formed JSON object with the following format.
    8. Return the JSON response without using code block formatting. The response should be directly loadable as JSON.
    9. Generate a SQL query based on the given prompt. Ensure that the SQL query includes the column names in the results.
       For example, if the prompt is 'Get the count of students from the PERSON table,' the SQL query should be: SELECT COUNT(*) AS StudentCount FROM PERSON WHERE Discriminator='Student'. The result should include the column name 'StudentCount'.
    10. Use SQL 'AS' statement to assign a new name temporarily to a table column or even a table wherever needed.
    11. Answer the question while maintaining consistency with the previous conversation.
    12. Please put your polite, kind, detailed whole explanation in 'explanation:' in JSON Formant


    ===Response Format
    {{
        "query": "SELECT * FROM PERSON",
        "explanation": "The prompt "how. many cat based on the paw?" seems to be unrelated to the provided database schema and tables. 
        The conversation appears to be about managing courses, students, instructors, departments, and grades in an educational institution.
        If you could provide more context or clarify what you mean by "cat" and "paw," I'd be happy to assist you with a relevant SQL query. 
"
    }}

    ===Question
    {query}
    """
    return prompt_template


def generate_refine_sql_script(query, text, formatted_error_history, context):
    prompt_template = f"""
    You are a MSSQL expert.

    Generate a MSSQL query to answer the question. Your response should ONLY be based on the given context and follow the response guidelines and format instructions.

    ===Tables
    {text}
    
    ===Previous Conversation
    {context}

    ===Response Guidelines
    1. If the provided context is sufficient, generate a valid query enclosed in a string without any explanations for the question.
    2. If the provided context is insufficient, explain why it can't be generated.
    3. Use the most relevant table(s).
    4. Only use the provided table names and column names; do not use any other names.
    5. Format the query before responding.
    6. Ensure the SQL query is executable without any modifications.
    7. The SQL query must be written as a single statement without using scalar variables.
    8. Always respond with a valid well-formed JSON object with the following format.
    9. Return the JSON response without using code block formatting. The response should be directly loadable as JSON.
    10. Generate a SQL query based on the given prompt. Ensure that the SQL query includes the column names in the results.
        For example, if the prompt is 'Get the count of students from the PERSON table,' the SQL query should be: SELECT COUNT(*) AS StudentCount FROM PERSON WHERE Discriminator='Student'. The result should include the column name 'StudentCount'.
    11. Use SQL 'AS' statement to assign a new name temporarily to a table column or even a table wherever needed.
    12. Answer the question while maintaining consistency with the previous conversation.

    ===Response Format
    {{
        "query": "SELECT * FROM PERSON",
        "explanation": "The SQL query retrieves all columns and rows from the `Person` table."
    }}

    ===Question
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


def generate_data_summary_prompt(data: str):
    template = f"""
    You are an expert summarizer.

    Your job is to produce a concise summary based on the provided data. 
    Follow the response guidelines and format instructions.

    ===Data
    {data}

    ===Response Guidelines
    1. Summarize the information in the data clearly and concisely.
    2. Only include the most relevant and important information.
    3. Format the summary in complete sentences and in a professional manner.
    """
    return template


def generate_combined_summary_prompt(current_summary: str, previous_summaries: str):
    template = f"""
    You are an expert summarizer.

    Your job is to produce a final, concise summary based on the current summary and the previously summarized content. 
    Follow the response guidelines and format instructions.

    ===Current Summary
    {current_summary}

    ===Previous Summaries
    {previous_summaries}

    ===Response Guidelines
    1. Combine the information from the current summary and the previous summaries.
    2. Ensure the final summary is clear, concise, and comprehensive.
    3. Only include the most relevant and important information.
    4. Format the final summary in complete sentences and in a professional manner.
    """
    return template


def generate_conversation(query: str):
    template = f"""
    You are a MSSQL expert.
    
    1. When engaging in general conversation, be polite, friendly, and informative.
    2. Always maintain your identity as an intelligent assistant designed to help with SQL and database-related tasks.

    User: "{query}"
        
    ===Response Format
    {{
        "answer" : "Your answer here"
    }}

    """
    return template

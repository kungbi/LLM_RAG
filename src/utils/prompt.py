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

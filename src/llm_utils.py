from langchain_core.prompts import ChatPromptTemplate
from langchain_core.runnables import RunnablePassthrough
from langchain_core.output_parsers import StrOutputParser
from langchain_openai import ChatOpenAI
from src.sql_utils import sqlite_table_schema, run_query, get_schema_description

# SQL Chain integrating the user-question and LLM and getting the corresponding SQL Query
def get_sql_chain(database_path, schema_description, table_name):
    template = """
    You are a data analyst at a company. You are interacting with a user who is asking you questions about the company's database.
    Based on the table schema below, write a SQL query that would answer the user's question. Take the conversation history into account.
    The SQL database has the name {TABLE_NAME}.

    <SCHEMA>{schema}</SCHEMA>

    Here are the details of what each column means:
    {schema_description}

    Conversation History: {chat_history}
    
    Write only the SQL query and nothing else. Do not wrap the SQL query in any other text, not even backticks.
    
    For example:
    Question: How many entries of records are present?
    SQL Query: SELECT COUNT(*) FROM {TABLE_NAME};
    Question: List all the unique regions.
    SQL Query: SELECT DISTINCT "Region" FROM {TABLE_NAME};
    Question: Give me the number of projects which were completed in 2016?
    SQL Query: SELECT COUNT(*) FROM {TABLE_NAME} WHERE strftime('%Y', completion_date) = '2016';
    
    Your turn:
    
    Question: {question}
    SQL Query:
    """
    
    prompt = ChatPromptTemplate.from_template(template)
    llm = ChatOpenAI(model="gpt-4o")
    
    def get_schema(_):
        return sqlite_table_schema(database_path, table_name)
    
    def get_schema_description_callable(_):
        return get_schema_description(schema_description)
    
    def get_table_name(_):
        return table_name
    
    return (
        RunnablePassthrough.assign(
            schema=get_schema,
            TABLE_NAME=get_table_name,
            schema_description=get_schema_description_callable
        )
        | prompt
        | llm
        | StrOutputParser()
    )

# To get the response from LLM by integrating DB, SQL Query and the User Question
def get_response(user_query: str, database_path: str, schema_description: str, table_name:str, chat_history: list):
    sql_chain = get_sql_chain(database_path, schema_description, table_name)

    # print("SQL Chain: ", sql_chain)
    # print()

    template = """
    You are a data analyst at a company. You are interacting with a user who is asking you questions about the company's database.
    Based on the table schema below, question, sql query, and sql response, write a natural language response.
    <SCHEMA>{schema}</SCHEMA>

    Conversation History: {chat_history}
    SQL Query: <SQL>{query}</SQL>
    User question: {question}
    SQL Response: {response}
    """
  
    prompt = ChatPromptTemplate.from_template(template)
    llm = ChatOpenAI(model="gpt-4o")
  
    chain = (
        RunnablePassthrough.assign(query=sql_chain).assign(
            schema=lambda _: sqlite_table_schema(database_path, table_name),
            response=lambda vars: run_query(database_path, vars["query"]),
        )
        | prompt
        | llm
        | StrOutputParser()
    )
  
    return chain.invoke({
        "question": user_query,
        "chat_history": chat_history,
    })
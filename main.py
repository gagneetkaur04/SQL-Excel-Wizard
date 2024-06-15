import os
import logging as log
import streamlit as st
from dotenv import load_dotenv
from src.sql_utils import *
from src.llm_utils import *
from langchain_core.messages import AIMessage, HumanMessage
from src.excelToSql import convert_excel_to_sqlite

# def handle_upload():
#     # SIDEBAR
#     st.sidebar.subheader("Upload Files")
    
#     db_name = st.sidebar.text_input("Enter the name of your database.")
#     table_name = st.sidebar.text_input("Enter the name of your table (sheet name).")
    
#     excel_file = st.sidebar.file_uploader("Choose an Excel file", type=["xlsx"])
#     schema_file = st.sidebar.file_uploader("Choose a schema description file", type=["txt"])

#     excel_path = ""
#     schema_path = ""
#     db_path = ""

#     if excel_file is not None and schema_file is not None:
#         os.makedirs("db", exist_ok=True)

#         excel_path = os.path.join("db", excel_file.name)
#         schema_path = os.path.join("db", schema_file.name)
#         db_path = f"{os.path.join('db', db_name)}.db"
        
#         # Save the uploaded files
#         with open(excel_path, "wb") as f:
#             f.write(excel_file.getbuffer())
        
#         with open(schema_path, "wb") as f:
#             f.write(schema_file.getbuffer())
        
#         st.sidebar.success("Files successfully uploaded!")

#     # Convert the uploaded Excel to SQLite
#     if st.sidebar.button("Convert to SQL DB") :
#         convert_excel_to_sqlite(file_path=excel_path, sheet_name=table_name, db_name=db_path, table_name=table_name)
#         st.sidebar.success("SQL Database is ready!")
#         print('SQL Database is ready')

#     return db_path, schema_path, table_name

def handle_upload():
    # SIDEBAR
    st.sidebar.subheader("Upload Files")
    
    db_name = st.sidebar.text_input("Enter the name of your database.")
    table_name = st.sidebar.text_input("Enter the name of your table (sheet name).")
    
    excel_file = st.sidebar.file_uploader("Choose an Excel file", type=["xlsx"])
    schema_file = st.sidebar.file_uploader("Choose a schema description file", type=["txt"])

    excel_path = ""
    schema_path = ""
    db_path = ""

    if db_name and table_name and excel_file and schema_file:
        os.makedirs("db", exist_ok=True)

        excel_path = os.path.join("db", excel_file.name)
        schema_path = os.path.join("db", schema_file.name)
        db_path = f"{os.path.join('db', db_name)}.db"

        # Save the uploaded files if they do not exist
        if not os.path.exists(excel_path):
            with open(excel_path, "wb") as f:
                f.write(excel_file.getbuffer())
        else : 
            st.sidebar.warning("Excel file already exists.")
        
        if not os.path.exists(schema_path):
            with open(schema_path, "wb") as f:
                f.write(schema_file.getbuffer())
        else :
            st.sidebar.warning("Schema file already exists.")
    
    if st.sidebar.button("Convert to SQL DB"):
        if not os.path.exists(db_path):
            convert_excel_to_sqlite(file_path=excel_path, sheet_name=table_name, db_name=db_path, table_name=table_name)
            st.sidebar.success("SQL Database is ready!")
            print('SQL Database is ready')
        else:
            st.sidebar.warning("SQL Database already exists.")
    
    return db_path, schema_path, table_name


def main():
    log.basicConfig(level=log.INFO)
    load_dotenv()

    st.set_page_config(page_title='Talk with SQL', page_icon=':speech_balloon:')
    st.title('Talk with SQL')

    db_path, schema_path, table_name = handle_upload()

    if "chat_history" not in st.session_state:
        st.session_state.chat_history = [
            AIMessage(content="Hello! I'm a SQL assistant. Ask me anything about your database!"),
        ]
    
    for message in st.session_state.chat_history:
        if isinstance(message, AIMessage):
            with st.chat_message("AI"):
                st.markdown(message.content)
        elif isinstance(message, HumanMessage):
            with st.chat_message("Human"):
                st.markdown(message.content)

    user_query = st.chat_input("Type a message...")

    if user_query is not None and user_query.strip() != "":
        st.session_state.chat_history.append(HumanMessage(content=user_query))
        
        with st.chat_message("Human"):
            st.markdown(user_query)
            
        with st.chat_message("AI"):
            response = get_response(user_query, db_path, schema_path, table_name, st.session_state.chat_history)
            st.markdown(response)
            
        st.session_state.chat_history.append(AIMessage(content=response)) 

if __name__ == '__main__':
    main()
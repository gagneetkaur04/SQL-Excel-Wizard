import streamlit as st
import sqlite3
import logging as log


# To get the schema of the table
def sqlite_table_schema(database_path, name):
    with sqlite3.connect(database_path) as conn:
        cursor = conn.execute("SELECT sql FROM sqlite_master WHERE name=?;", [name])
        sql = cursor.fetchone()
        return sql[0] if sql else None


# Description of the Schema
def get_schema_description(file_path):
    with open(file_path, 'r') as file:
        return file.read()


# To run the SQL query on the DB
def run_query(database_path, query):
    print("SQL Query: ", query)

    with sqlite3.connect(database_path) as conn:
        cursor = conn.cursor()
        cursor.execute(query)

        answer = cursor.fetchall()
        print("Fetchall: ", answer)

        return answer
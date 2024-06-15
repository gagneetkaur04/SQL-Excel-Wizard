import sqlite3
import pandas as pd
import numpy as np

def convert_excel_to_sqlite(file_path, sheet_name, db_name, table_name):
    df = pd.read_excel(file_path, sheet_name=sheet_name)
    df = df.replace({np.nan: None}) # Replacing null values
    
    # Convert datetime columns to strings
    for col in df.columns:
        if pd.api.types.is_datetime64_any_dtype(df[col]):
            df[col] = df[col].astype(str)
    
    # Connect to SQLite
    connection = sqlite3.connect(db_name)
    cursor = connection.cursor()
    
    # Dynamically create a table
    columns = df.columns
    col_types = []
    
    for col in columns:
        if df[col].dtype == 'int64':
            col_type = 'INT'
        elif df[col].dtype == 'float64':
            col_type = 'FLOAT'
        elif pd.api.types.is_datetime64_any_dtype(df[col]):
            col_type = 'DATETIME'
        else:
            col_type = 'VARCHAR(255)'
        col_types.append(f'"{col}" {col_type}')
    
    create_table_query = f'CREATE TABLE IF NOT EXISTS {table_name} ({", ".join(col_types)});'
    cursor.execute(create_table_query)
    connection.commit()
    
    columns_part = ', '.join([f'"{col}"' for col in columns])
    placeholders_part = ', '.join(['?' for _ in columns])
    insert_query = f'INSERT INTO {table_name} ({columns_part}) VALUES ({placeholders_part});'
    
    for index, row in df.iterrows():
        row_data = tuple(row[col] if isinstance(row[col], (int, float, str)) else str(row[col]) for col in columns)
        cursor.execute(insert_query, row_data)
        connection.commit()

    connection.close()
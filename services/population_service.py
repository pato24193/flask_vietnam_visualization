import pandas as pd
import sqlite3

def read_population_data_from_excel(file_path: str) -> pd.DataFrame:
    # Read the Excel file, starting from the appropriate row
    df = pd.read_excel(file_path, header=3)
    # Rename the columns for clarity
    df.columns = ['province_name', 'population_2021', 'population_2022', 'population_2023']
    return df


def save_population_data_to_sqlite(df: pd.DataFrame, db_path: str = 'data_sqlite.db'):
    # Connect to the SQLite database
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    # Create the table if it doesn't exist
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS populations (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            province_name TEXT,
            population_2021 REAL,
            population_2022 REAL,
            population_2023 REAL
        )
    ''')
    
    cursor.execute('''
        DELETE FROM populations
    ''')
        
    # Insert the data from the DataFrame into the SQLite database
    for _, row in df.iterrows():
        cursor.execute('''
            INSERT INTO populations (province_name, population_2021, population_2022, population_2023)
            VALUES (?, ?, ?, ?)
        ''', (row['province_name'], row['population_2021'], row['population_2022'], row['population_2023']))

    # Commit and close the connection
    conn.commit()
    conn.close()

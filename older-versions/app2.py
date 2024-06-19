#this app store the file hashes in a database (FileHashDB) - recommended

from flask import Flask, render_template, request, redirect, url_for
import os
import logging
import json
from datetime import datetime
from calculate_hash import calculate_hash
import pyodbc  # Import pyodbc for SQL Server connection

app = Flask(__name__)

# Configuration for SQL Server connection
server = 'DESKTOP-TONH6GQ'  # Replace with your SQL Server instance name
database = 'FileHashDB'      # Replace with your database name
username = 'sa'              # Replace with your SQL Server username
password = '1234'            # Replace with your SQL Server password
driver = '{ODBC Driver 17 for SQL Server}'  # Replace with the appropriate driver version

# Establish a connection to SQL Server
def create_connection():
    try:
        conn = pyodbc.connect(f'DRIVER={driver};SERVER={server};DATABASE={database};UID={username};PWD={password}')
        return conn
    except pyodbc.Error as e:
        logging.error(f"Error connecting to SQL Server: {e}")
        return None

# Function to store file hash in SQL Server
def store_hash(file_path, algorithm='sha256'):
    conn = create_connection()
    if not conn:
        return "Error: Failed to connect to the database."
    
    try:
        if not os.path.exists(file_path):
            error_msg = f"Error: File '{file_path}' does not exist."
            logging.error(error_msg)
            return error_msg

        hash_value = calculate_hash(file_path, algorithm)
        if hash_value is None:
            return f"Error: Failed to calculate hash for '{file_path}'."

        timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        cursor = conn.cursor()

        # Check if a record with the same file_path and algorithm exists
        cursor.execute('''
            SELECT COUNT(*) FROM FileHashes WHERE file_path = ? AND algorithm = ?
        ''', (file_path, algorithm))
        count = cursor.fetchone()[0]

        if count > 0:
            # Update existing record
            cursor.execute('''
                UPDATE FileHashes
                SET hash = ?, timestamp = ?
                WHERE file_path = ? AND algorithm = ?
            ''', (hash_value, timestamp, file_path, algorithm))
        else:
            # Insert new record
            cursor.execute('''
                INSERT INTO FileHashes (file_path, hash, algorithm, timestamp)
                VALUES (?, ?, ?, ?)
            ''', (file_path, hash_value, algorithm, timestamp))
        
        conn.commit()

        logging.info(f'Stored hash for {file_path} ({timestamp}): {hash_value}')
        return f'Hash stored successfully for {file_path}.'
    
    except Exception as e:
        error_msg = f"Error: Exception occurred while processing {file_path}: {str(e)}"
        logging.error(error_msg)
        return error_msg
    
    finally:
        conn.close()


# Function to verify file hash in SQL Server
def verify_file(file_path, algorithm='sha256'):
    conn = create_connection()
    if not conn:
        return "Error: Failed to connect to the database."
    
    try:
        cursor = conn.cursor()
        cursor.execute('''
            SELECT hash FROM FileHashes WHERE file_path = ? AND algorithm = ?
        ''', (file_path, algorithm))
        row = cursor.fetchone()

        if not row:
            return f'Error: Unable to locate the Hash of File: {file_path} for algorithm {algorithm}'
        
        if not os.path.exists(file_path):
            error_msg = f"Error: file path has been changed!"
            logging.error(error_msg)
            return error_msg

        stored_hash = row[0]
        current_hash = calculate_hash(file_path, algorithm)

        if current_hash == stored_hash:
            return f'{file_path} is safe for algorithm {algorithm}.'
        else:
            return f'{file_path} has been compromised for algorithm {algorithm}.'

    except Exception as e:
        error_msg = f"Error: Exception occurred while verifying {file_path} for algorithm {algorithm}: {str(e)}"
        logging.error(error_msg)
        return error_msg
    
    finally:
        conn.close()


# Route for rendering index.html template
@app.route('/')
def index():
    return render_template('index.html')

# Route for handling POST requests from the form
@app.route('/process', methods=['POST'])
def process():
    file_path = request.form['file_path']
    algorithm = request.form['algorithm']
    action = request.form['action']

    if action == 'store':
        result = store_hash(file_path, algorithm)
    elif action == 'verify':
        result = verify_file(file_path, algorithm)
    else:
        result = "Unknown action requested."
    
    return render_template('index.html', result=result)

if __name__ == '__main__':
    app.run(debug=True)

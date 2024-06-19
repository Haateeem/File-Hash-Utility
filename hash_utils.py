import hashlib
import logging
import pyodbc
from datetime import datetime

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

def calculate_hash(file, algorithm='sha256'):
    try:
        hasher = hashlib.new(algorithm)
        file.seek(0)  # Ensure we're reading from the beginning of the file
        for chunk in iter(lambda: file.read(4096), b''):
            hasher.update(chunk)
        file.seek(0)  # Reset file pointer to the beginning after reading
        return hasher.hexdigest()
    except Exception as e:
        logging.error(f"Error calculating hash for the uploaded file: {e}")
        return None

# Function to store file hash in SQL Server
def store_hash(file, filename, algorithm='sha256'):
    conn = create_connection()
    if not conn:
        result = "Error: Failed to connect to the database."
        return result

    try:
        hash_value = calculate_hash(file, algorithm)
        if hash_value is None:
            result = f"Error: Failed to calculate hash for the uploaded file."
            return result

        timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        cursor = conn.cursor()

        # Check if a record with the same content identifier and algorithm exists
        cursor.execute('''
            SELECT COUNT(*) FROM FileHashes WHERE content_identifier = ? AND algorithm = ?
        ''', (hash_value, algorithm))
        count = cursor.fetchone()[0]

        if count > 0:
            # Update existing record
            cursor.execute('''
                UPDATE FileHashes
                SET file_path = ?, timestamp = ?
                WHERE content_identifier = ? AND algorithm = ?
            ''', (filename, timestamp, hash_value, algorithm))
        else:
            # Insert new record
            cursor.execute('''
                INSERT INTO FileHashes (file_path, hash, algorithm, content_identifier, timestamp)
                VALUES (?, ?, ?, ?, ?)
            ''', (filename, hash_value, algorithm, hash_value, timestamp))
        
        conn.commit()

        logging.info(f'Stored hash for {filename} ({timestamp}): {hash_value}')
        result = f'Hash stored successfully for {filename}.'
        return result

    except Exception as e:
        error_msg = f"Error: Exception occurred while processing the uploaded file: {str(e)}"
        logging.error(error_msg)
        return error_msg

    finally:
        conn.close()

# Function to verify file hash in SQL Server
def verify_file(file, algorithm='sha256'):
    conn = create_connection()
    if not conn:
        result = "Error: Failed to connect to the database."
        return result

    try:
        current_hash = calculate_hash(file, algorithm)
        if current_hash is None:
            result = f"Error: Failed to calculate hash for the uploaded file."
            return result
        
        cursor = conn.cursor()
        cursor.execute('''
            SELECT file_path FROM FileHashes WHERE content_identifier = ? AND algorithm = ?
        ''', (current_hash, algorithm))
        row = cursor.fetchone()

        if not row:
            result = f'No Match Found! This file may have been tampered! - {algorithm}'
            return result

        original_file_path = row[0]
        result = f'Match Found with: {original_file_path} - {algorithm}.'
        return result

    except Exception as e:
        error_msg = f"Error: Exception occurred while verifying the uploaded file for algorithm {algorithm}: {str(e)}"
        logging.error(error_msg)
        return error_msg

    finally:
        conn.close()

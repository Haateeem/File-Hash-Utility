# depreciated
# this app version stores the file hashes in a json file, (not recommended)

from flask import Flask, render_template, request, redirect, url_for
import os
import logging
import json
from datetime import datetime
from calculate_hash import calculate_hash

app = Flask(__name__)

JSON_FILE = 'hash_store.json'

def load_hash_store():
    if os.path.exists(JSON_FILE):
        with open(JSON_FILE, 'r') as json_file:
            return json.load(json_file)
    else:
        return {}

def store_hash_store(hash_store):
    with open(JSON_FILE, 'w') as json_file:
        json.dump(hash_store, json_file, indent=4)

hash_store = load_hash_store()

def store_hash(file_path, algorithm='sha256'):
    abs_file_path = os.path.abspath(file_path)  # Convert to absolute path
    if not os.path.exists(abs_file_path):
        error_msg = f"Error: File '{abs_file_path}' does not exist."
        logging.error(error_msg)
        return error_msg

    try:
        hash_value = calculate_hash(abs_file_path, algorithm)
        if hash_value is not None:
            timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            hash_store[abs_file_path] = {'hash': hash_value, 'timestamp': timestamp, 'algorithm': algorithm}
            store_hash_store(hash_store)
        
            logging.info(f'Stored hash for {abs_file_path} ({timestamp}): {hash_value}')
            return f'Hash stored successfully!'
        
    except Exception as e:
        error_msg = f"Error: Exception occurred while processing {abs_file_path}: {str(e)}"
        logging.error(error_msg)
        return error_msg

def verify_file(file_path, algorithm='sha256'):
    if file_path not in hash_store:
        error_msg = f'Error: Unable to locate the Hash of File: {file_path}'
        logging.error(error_msg)
        return error_msg
    
    if not os.path.exists(file_path):
        error_msg = f"Error: File '{file_path}' does not exist."
        logging.error(error_msg)
        return error_msg

    current_hash = calculate_hash(file_path, algorithm)
    stored_hash = hash_store[file_path]['hash']
    if current_hash == stored_hash:
        return f'{file_path} is safe.'
    else:
        return f'{file_path} has been compromised.'

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/process', methods=['POST'])
def process():
    file_path = request.form['file_path']
    algorithm = request.form['algorithm']
    action = request.form['action']

    if action == 'store':
        result = store_hash(file_path, algorithm)
    elif action == 'verify':
        result = verify_file(file_path, algorithm)
        
    """     
        if result is True:
            result = f'{file_path} is safe.'
        elif result is False:
            result = f'{file_path} has been compromised.'
        else:
            result = f'Unable to locate the Hash of File: {file_path}' """

    return render_template('index.html', result=result)

if __name__ == '__main__':
    app.run(debug=True)

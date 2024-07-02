#flask app to run project on web browser
#execute python3 app.py in terminal, copy the 

from flask import Flask, render_template, request, redirect, url_for, jsonify
import os
import subprocess
import logging
import hashlib
from hash_utils import store_hash, verify_file

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = 'uploads'
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

# Route for rendering index.html template
""" @app.route('/')
def index():
    return render_template('index.html') """

@app.route('/')
def index():
    user_agent = request.headers.get('User-Agent').lower()
    if 'mobile' in user_agent:
        return render_template('mobile-template.html')
    else:
        return render_template('index.html')

# Route for handling POST requests from the form
@app.route('/process', methods=['POST'])
def process():
    if 'file' not in request.files:
        return redirect(request.url)
    
    file = request.files['file']
    algorithm = request.form['algorithm']
    action = request.form['action']

    if file.filename == '':
        return redirect(request.url)
    
    filename = file.filename

    if action == 'store':
        result = store_hash(file, filename, algorithm)
    elif action == 'verify':
        result = verify_file(file, algorithm)
    else:
        result = "Unknown action requested."
    
    return render_template('index.html', result=result)

@app.route('/calculate', methods=['POST'])
def calculate():
    input_text = request.form['input']
    algorithm = request.form['algorithm']

    # Calculate hash
    hash_func = hashlib.new(algorithm)
    hash_func.update(input_text.encode('utf-8'))
    hash_result = hash_func.hexdigest()

    return render_template('index.html', result2=hash_result)


if __name__ == '__main__':
    app.run(host='0.0.0.0', debug=True)

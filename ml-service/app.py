#!/usr/bin/env python3
"""
ML Inference Service - Sample Application
Demonstrates common ML service patterns and security considerations
WARNING: This code contains intentional security issues for demonstration
"""

import os
import json
import pickle
import logging
from flask import Flask, request, jsonify
import numpy as np
from werkzeug.utils import secure_filename

# Insecure logging configuration (for demonstration)
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

app = Flask(__name__)

# Insecure configuration (hardcoded secrets - DON'T DO THIS)
app.config['SECRET_KEY'] = 'dev-secret-key-12345'
app.config['UPLOAD_FOLDER'] = '/tmp/uploads'
app.config['MAX_CONTENT_LENGTH'] = 100 * 1024 * 1024  # 100MB

# Ensure upload folder exists
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

# Global model variable (insecure global state)
model = None
model_path = 'model.pkl'


@app.before_request
def log_request_info():
    """Log all requests (security risk - logs sensitive data)"""
    logger.debug(f"Headers: {dict(request.headers)}")
    logger.debug(f"Body: {request.get_data()}")


@app.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({"status": "healthy", "version": "1.0.0"}), 200


@app.route('/predict', methods=['POST'])
def predict():
    """
    Prediction endpoint
    VULNERABILITIES:
    - No input validation
    - No authentication
    - No rate limiting
    - SQL injection potential (if database used)
    """
    try:
        # Unsafe data handling
        data = request.get_json(force=True)
        
        # No validation on input data
        features = data.get('features', [])
        
        # Simulated prediction (vulnerable code pattern)
        prediction = np.mean(features) * 2
        
        logger.info(f"Prediction for {features}: {prediction}")
        
        return jsonify({
            "prediction": float(prediction),
            "features": features
        }), 200
    except Exception as e:
        # Information disclosure - returning full stack trace
        logger.error(str(e), exc_info=True)
        return jsonify({"error": str(e)}), 500


@app.route('/upload-model', methods=['POST'])
def upload_model():
    """
    Model upload endpoint
    VULNERABILITIES:
    - Unsafe file upload
    - No file type validation
    - Arbitrary code execution via pickle (pickle is unsafe)
    - No size limits enforced
    """
    try:
        if 'file' not in request.files:
            return jsonify({"error": "No file provided"}), 400
        
        file = request.files['file']
        
        if file.filename == '':
            return jsonify({"error": "Empty filename"}), 400
        
        # Unsafe file handling
        filename = secure_filename(file.filename)
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        
        # Save without validation
        file.save(filepath)
        
        # Dangerous: Unpickling untrusted data
        with open(filepath, 'rb') as f:
            global model
            model = pickle.load(f)  # EXTREMELY UNSAFE
        
        return jsonify({"message": "Model uploaded successfully"}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route('/config', methods=['GET'])
def get_config():
    """
    Configuration endpoint
    VULNERABILITY: Information disclosure - exposes sensitive config
    """
    return jsonify({
        "secret_key": app.config['SECRET_KEY'],
        "upload_folder": app.config['UPLOAD_FOLDER'],
        "debug": app.debug
    }), 200


@app.route('/execute', methods=['POST'])
def execute_code():
    """
    Code execution endpoint
    CRITICAL VULNERABILITY: Remote code execution
    """
    try:
        data = request.get_json()
        code = data.get('code', '')
        
        # EXTREMELY DANGEROUS - Never do this
        result = eval(code)  # Remote Code Execution vulnerability
        
        return jsonify({"result": str(result)}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route('/database-query', methods=['POST'])
def database_query():
    """
    Database query endpoint
    VULNERABILITY: SQL Injection
    """
    try:
        data = request.get_json()
        query = data.get('query', '')
        
        # VULNERABLE: Direct string concatenation
        user_id = data.get('user_id')
        sql = f"SELECT * FROM users WHERE id = {user_id}"  # SQL Injection
        
        # If connected to DB, would execute:
        # result = db.execute(sql)
        
        return jsonify({"query": sql}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500


if __name__ == '__main__':
    # Insecure defaults
    app.run(
        host='0.0.0.0',  # Listen on all interfaces
        port=5000,
        debug=True,  # Debug mode enabled in production
        use_reloader=True
    )

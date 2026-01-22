# Known Vulnerabilities in Demo Application

This document details the intentional vulnerabilities in the demo application for security scanning demonstration purposes.

## Python Dependencies Vulnerabilities

### Critical CVEs in requirements.txt

| Package | Version | CVE | Severity | Description |
|---------|---------|-----|----------|-------------|
| Flask | 0.12.3 | CVE-2018-1000656 | Critical | Insufficient entropy in generate_password_hash |
| Werkzeug | 0.11.0 | CVE-2016-9601 | High | Path traversal vulnerability |
| Jinja2 | 2.7.2 | CVE-2016-10516 | Critical | Sandbox escape vulnerability |
| Requests | 2.5.1 | CVE-2015-2296 | High | Unverified hostname SSL match |
| PyYAML | 5.1 | CVE-2020-1747 | Critical | Arbitrary code execution via load() |
| Pillow | 2.5.0 | CVE-2014-1932 | High | Image format buffer overflow |
| NumPy | 1.8.0 | Multiple | Medium | Data processing vulnerabilities |
| TensorFlow | 1.0.0 | CVE-2017-3506 | High | Model poisoning vulnerability |
| Cryptography | 0.7 | CVE-2015-3206 | Critical | ECDSA signature forgery |

## Dockerfile Vulnerabilities

### Dockerfile.insecure Contains

1. **Outdated Base Image (ubuntu:16.04)**
   - End of life since April 30, 2021
   - Contains 200+ known vulnerabilities
   - Missing security patches

2. **Root User Execution**
   ```dockerfile
   USER root
   ```
   - Runs container as root
   - If container is compromised, attacker has full system access
   - Violates principle of least privilege

3. **SSH Server Enabled**
   ```dockerfile
   RUN echo "PermitRootLogin yes" >> /etc/ssh/sshd_config
   ```
   - Increases attack surface
   - SSH not needed in containers
   - Root SSH login enabled (critical risk)

4. **Unpinned Dependency Versions**
   ```dockerfile
   RUN apt-get install -y python-pip curl wget git
   ```
   - No version pinning
   - Unpredictable builds
   - May pull vulnerable packages

5. **No Health Check**
   - No HEALTHCHECK instruction
   - Cannot detect container failures
   - Orchestrators cannot manage health

## Application Code Vulnerabilities

### app.py Security Issues

#### 1. Remote Code Execution
```python
@app.route('/execute', methods=['POST'])
def execute_code():
    code = request.get_json()['code']
    result = eval(code)  # CRITICAL: Remote code execution
    return jsonify({"result": result})
```
- **Risk:** Arbitrary code execution
- **Impact:** Complete system compromise
- **Fix:** Never use eval() on user input

#### 2. SQL Injection
```python
user_id = data.get('user_id')
sql = f"SELECT * FROM users WHERE id = {user_id}"  # SQL injection
```
- **Risk:** Database compromise
- **Impact:** Data theft, modification, deletion
- **Fix:** Use parameterized queries

#### 3. Unsafe Pickle Deserialization
```python
with open(filepath, 'rb') as f:
    model = pickle.load(f)  # CRITICAL: Arbitrary code execution
```
- **Risk:** Arbitrary code execution via malicious pickle files
- **Impact:** Complete compromise when loading untrusted models
- **Fix:** Use joblib.load with protocol version check, or use safetensors

#### 4. Insecure File Upload
```python
file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
```
- **Risk:** Path traversal, arbitrary file write
- **Impact:** Overwrite critical files
- **Fix:** Validate file types, use unique filenames

#### 5. Information Disclosure
```python
@app.route('/config', methods=['GET'])
def get_config():
    return jsonify({
        "secret_key": app.config['SECRET_KEY'],  # Exposes secrets
        "upload_folder": app.config['UPLOAD_FOLDER']
    })
```
- **Risk:** Sensitive information exposure
- **Impact:** Attacker gains configuration details
- **Fix:** Never expose sensitive config in responses

#### 6. Missing Authentication
```python
@app.route('/predict', methods=['POST'])
def predict():
    data = request.get_json(force=True)  # No authentication
```
- **Risk:** Unauthorized access to ML service
- **Impact:** Model extraction, resource abuse
- **Fix:** Implement API authentication (OAuth, API keys)

#### 7. Missing Input Validation
```python
features = data.get('features', [])
# No validation on input
```
- **Risk:** Invalid data, buffer overflow potential
- **Impact:** Prediction errors, potential DoS
- **Fix:** Validate input type, size, range

#### 8. Debug Mode in Production
```python
if __name__ == '__main__':
    app.run(debug=True)  # Never in production
```
- **Risk:** Detailed error information exposure
- **Impact:** Information disclosure for attackers
- **Fix:** Disable debug mode in production

#### 9. Hardcoded Secrets
```python
app.config['SECRET_KEY'] = 'dev-secret-key-12345'
```
- **Risk:** Secret exposure
- **Impact:** Session hijacking
- **Fix:** Use environment variables

#### 10. Listening on All Interfaces
```python
app.run(host='0.0.0.0')
```
- **Risk:** Unnecessary network exposure
- **Impact:** Network-wide access
- **Fix:** Listen on localhost or specific interface

## Remediation Examples

### Fix 1: Secure Dependencies
```python
# BEFORE (requirements.txt)
flask==0.12.3
werkzeug==0.11.0

# AFTER (requirements.txt)
flask==3.0.0
werkzeug==3.0.0
```

### Fix 2: Secure Dockerfile
```dockerfile
# Use specific secure base image
FROM python:3.9-slim

# Create non-root user
RUN useradd -m appuser
USER appuser

# Pin all versions
RUN pip install flask==3.0.0
```

### Fix 3: Secure Code
```python
# Secure prediction endpoint
from flask import request, jsonify
from functools import wraps

def require_api_key(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        api_key = request.headers.get('X-API-Key')
        if not api_key or api_key != os.getenv('API_KEY'):
            return jsonify({"error": "Unauthorized"}), 401
        return f(*args, **kwargs)
    return decorated_function

@app.route('/predict', methods=['POST'])
@require_api_key
def predict():
    try:
        data = request.get_json()
        
        # Input validation
        if not data or 'features' not in data:
            return jsonify({"error": "Missing features"}), 400
        
        features = data['features']
        if not isinstance(features, list) or len(features) > 100:
            return jsonify({"error": "Invalid features"}), 400
        
        # Safe inference
        result = model.predict(features)
        return jsonify({"prediction": result}), 200
    except ValueError as e:
        logger.warning(f"Validation error: {e}")
        return jsonify({"error": "Invalid input"}), 400
```

## Vulnerability Scan Results

### Expected Trivy Output (Insecure Image)

```
Total: 245 vulnerabilities
- CRITICAL: 15
- HIGH: 32
- MEDIUM: 98
- LOW: 100
```

### Expected Anchore Output (Insecure Image)

```
Policy evaluation results:
FAIL:
  - Policy rule: No critical CVEs (CRITICAL)
  - Policy rule: No root user (HIGH)
  - Policy rule: SSH port not exposed (CRITICAL)
WARN:
  - Policy rule: Unpinned versions (MEDIUM)
```

---

## Testing Vulnerability Detection

### Verify Trivy Detects Vulnerabilities

```bash
# Build insecure image
docker build -f docker/Dockerfile.insecure -t ml-service:insecure .

# Scan with Trivy
trivy image --severity CRITICAL,HIGH ml-service:insecure

# Expected: Multiple critical and high severity findings
```

### Verify CI/CD Gates

1. **Push to GitLab/GitHub**
2. **Pipeline should FAIL** on security stage
3. **Review error logs** to see detected vulnerabilities
4. **Cannot merge** until vulnerabilities fixed

---

**Note:** This document is for educational and demonstration purposes only.
Never use these vulnerable configurations in production systems.

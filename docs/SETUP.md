# Setup Instructions - DevSecOps ML Pipeline

## Complete Step-by-Step Setup Guide

### Prerequisites

Before starting, ensure you have:

- **Docker Desktop** (Windows/Mac) or Docker Engine (Linux)
- **Python 3.9+** with pip
- **Git** for version control
- **bash** shell (Windows users can use WSL2 or Git Bash)
- **4GB+ RAM** available for Docker
- **10GB+ disk space** for dependencies and images

### Step 1: Environment Setup

#### Windows Users (Using WSL2)

1. **Install WSL2:**
```powershell
wsl --install
```

2. **Install Docker Desktop** with WSL2 support:
   - Download from https://www.docker.com/products/docker-desktop
   - Enable WSL2 integration in settings

3. **Install Python:**
```bash
sudo apt-get update
sudo apt-get install python3.9 python3-pip
```

#### macOS Users

1. **Install Homebrew (if not installed):**
```bash
/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
```

2. **Install dependencies:**
```bash
brew install docker docker-compose python@3.9 git
brew install --cask docker
```

#### Linux Users (Ubuntu/Debian)

1. **Install Docker:**
```bash
curl -fsSL https://get.docker.com -o get-docker.sh
sudo sh get-docker.sh
sudo usermod -aG docker $USER
```

2. **Install Docker Compose:**
```bash
sudo curl -L "https://github.com/docker/compose/releases/latest/download/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
sudo chmod +x /usr/local/bin/docker-compose
```

3. **Install Python and Git:**
```bash
sudo apt-get update
sudo apt-get install python3.9 python3-pip git
```

### Step 2: Install Security Tools

#### Install Trivy

```bash
# macOS
brew install trivy

# Linux
curl -sfL https://raw.githubusercontent.com/aquasecurity/trivy/main/contrib/install.sh | sh -s -- -b /usr/local/bin

# Or use Docker (all platforms)
docker pull aquasec/trivy:latest
```

Verify installation:
```bash
trivy version
```

#### Install Anchore Tools

```bash
# Install Anchore CLI
curl -sSfL https://anchorectl.anchore.io/install.sh | sh -s -- -b /usr/local/bin

# Or via pip
pip install anchore-engine
```

#### Install Python Security Tools

```bash
pip install --upgrade pip
pip install safety bandit semgrep cyclonedx-bom pip-audit
```

Verify installations:
```bash
safety --version
bandit --version
semgrep --version
```

### Step 3: Clone and Navigate to Project

```bash
# Navigate to your projects directory
cd ~/projects  # or your preferred location

# The project is already created in:
cd "c:\Users\pushp\OneDrive\Desktop\Reaidy.io-MLOps\devsecops-ml-pipeline"

# Or clone from repository
git clone <repository-url> devsecops-ml-pipeline
cd devsecops-ml-pipeline
```

### Step 4: Build Docker Images

#### Build Secure Image

```bash
# Using build script
bash docker/build-secure.sh

# Or manually
docker build -f docker/Dockerfile.secure \
  -t ml-service:secure \
  -t ml-service:latest \
  .
```

#### Build Insecure Image (for testing)

```bash
# Using build script
bash docker/build-insecure.sh

# Or manually
docker build -f docker/Dockerfile.insecure \
  -t ml-service:insecure \
  .
```

Verify images:
```bash
docker images | grep ml-service
```

### Step 5: Run Local Security Scans

#### Method 1: Using Provided Script

```bash
# Make script executable (Unix/Linux/macOS)
chmod +x scripts/scan-local.sh

# Run the comprehensive scan
bash scripts/scan-local.sh

# Results will be in: scan-results-YYYYMMDD-HHMMSS/
```

#### Method 2: Individual Scans

**Python Dependencies:**
```bash
safety check --file ml-service/requirements.txt
```

**Static Code Analysis:**
```bash
bandit -r ml-service/ -f json -o bandit-report.json
```

**Dockerfile Analysis:**
```bash
trivy config docker/
```

**Container Image Scanning:**
```bash
trivy image ml-service:secure
trivy image ml-service:insecure
```

**Generate SBOM:**
```bash
trivy image --format cyclonedx --output sbom.json ml-service:secure
```

### Step 6: Set Up CI/CD Pipeline

#### For GitLab

1. **Push project to GitLab:**
```bash
git init
git add .
git commit -m "Initial DevSecOps setup"
git remote add origin https://gitlab.com/your-username/devsecops-ml-pipeline.git
git push -u origin main
```

2. **Create `.gitlab-ci.yml`:**
```bash
cp ci-config/.gitlab-ci.yml .
```

3. **Push to trigger pipeline:**
```bash
git add .gitlab-ci.yml
git commit -m "Add CI/CD pipeline"
git push origin main
```

4. **View pipeline:**
   - Go to your GitLab project
   - Navigate to CI/CD → Pipelines
   - Watch pipeline stages execute

#### For GitHub

1. **Push project to GitHub:**
```bash
git init
git add .
git commit -m "Initial DevSecOps setup"
git remote add origin https://github.com/your-username/devsecops-ml-pipeline.git
git push -u origin main
```

2. **Create workflows directory:**
```bash
mkdir -p .github/workflows
```

3. **Add security workflow:**
```bash
cp ci-config/security.yml .github/workflows/
```

4. **Push to trigger workflow:**
```bash
git add .github/workflows/
git commit -m "Add security workflow"
git push origin main
```

5. **View results:**
   - Go to your GitHub repo
   - Navigate to Actions tab
   - See "ML Service Security Scan Pipeline"

### Step 7: Local Development Setup

#### Create Python Virtual Environment

```bash
# Create virtual environment
python3 -m venv venv

# Activate virtual environment
# On macOS/Linux:
source venv/bin/activate

# On Windows (Command Prompt):
venv\Scripts\activate

# On Windows (PowerShell):
venv\Scripts\Activate.ps1
```

#### Install Dependencies

```bash
# Install secure dependencies
pip install -r ml-service/requirements-secure.txt

# Install development tools
pip install pytest pytest-cov pytest-docker
```

#### Run Application

```bash
# Using development server
python ml-service/app.py

# Or using Gunicorn (production-like)
gunicorn --bind 0.0.0.0:5000 ml-service.app:app
```

### Step 8: Verify Setup

#### Check All Tools

```bash
echo "=== Checking Docker ==="
docker --version
docker ps

echo "=== Checking Security Tools ==="
trivy version
safety --version
bandit --version

echo "=== Checking Python ==="
python3 --version
pip list | grep -E "(flask|trivy|safety|bandit)"

echo "=== Checking Project ==="
ls -la
docker images | grep ml-service
```

#### Run Quick Scan

```bash
# Quick vulnerability scan
trivy image ml-service:secure

# Expected output:
# 0-5 vulnerabilities if properly configured
```

### Step 9: Configure for Your Environment

#### Update GitLab CI Variables

In `.gitlab-ci.yml`, set:
```yaml
variables:
  REGISTRY: your-registry.example.com
  IMAGE_NAME: "your-org/ml-service"
```

#### Update GitHub Secrets

In GitHub repo settings, add secrets:
- `REGISTRY` = ghcr.io
- `IMAGE_NAME` = your-org/ml-service

#### Customize Security Policies

Edit `security/trivy.yaml`:
```yaml
vulnerability:
  severity:
    - CRITICAL
    - HIGH
    # - MEDIUM  # Uncomment to include MEDIUM
```

Edit `security/anchore-policy.yaml` to add custom rules.

### Step 10: Test the Pipeline

#### Test Local Scan

```bash
# Should complete without errors
bash scripts/scan-local.sh

# Check results
ls -la scan-results-*/
cat scan-results-*/trivy-*.json | python -m json.tool | head -50
```

#### Test CI/CD Pipeline

```bash
# Push a small change
git add -A
git commit -m "Test security pipeline"
git push origin main

# For GitLab: Check CI/CD → Pipelines
# For GitHub: Check Actions tab
# Pipeline should fail on insecure image, pass on secure image
```

### Troubleshooting

#### Issue: Docker daemon not running

**Solution:**
```bash
# macOS
open -a Docker

# Linux
sudo systemctl start docker

# Windows
# Start Docker Desktop from Applications
```

#### Issue: Permission denied for docker

**Solution (Linux):**
```bash
sudo usermod -aG docker $USER
newgrp docker
```

#### Issue: Trivy database download fails

**Solution:**
```bash
# Update Trivy database manually
trivy image --download-db-only

# Or skip online check
trivy image --skip-update ml-service:latest
```

#### Issue: CI/CD pipeline fails to push image

**Solution:**
1. Check registry credentials
2. Ensure registry is accessible
3. Check image name format
4. Review CI/CD logs for details

#### Issue: Python packages not installing

**Solution:**
```bash
# Upgrade pip
pip install --upgrade pip setuptools wheel

# Try installing again
pip install -r ml-service/requirements.txt --no-cache-dir
```

### Next Steps

1. **Explore Documentation:**
   - Read [README.md](../docs/README.md) for comprehensive guide
   - Review [VULNERABILITIES.md](../docs/VULNERABILITIES.md) to understand demo issues

2. **Customize for Your Needs:**
   - Update security policies in `security/`
   - Modify CI/CD pipelines for your infrastructure
   - Add custom scanning rules

3. **Integrate with Your Workflow:**
   - Set up branch protection rules
   - Configure notifications
   - Set up scheduled scans

4. **Monitor and Maintain:**
   - Review scan results regularly
   - Update dependencies
   - Track security metrics

---

**Need Help?**
- Check troubleshooting section above
- Review tool documentation
- Open an issue in the repository


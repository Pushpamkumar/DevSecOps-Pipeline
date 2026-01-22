# DevSecOps Integration for ML Pipelines - Complete Guide

## Overview

This project demonstrates comprehensive DevSecOps integration for ML service pipelines, including:
- Container security scanning using Trivy and Anchore
- Python dependency vulnerability detection
- CI/CD pipeline security gates using GitLab CI and GitHub Actions
- Infrastructure-as-Code security analysis
- Secret detection and management
- Comprehensive policy enforcement

## Table of Contents

1. [Project Structure](#project-structure)
2. [Getting Started](#getting-started)
3. [Tools Overview](#tools-overview)
4. [Configuration Guide](#configuration-guide)
5. [Running Security Scans](#running-security-scans)
6. [CI/CD Pipeline Integration](#cicd-pipeline-integration)
7. [Remediation Guide](#remediation-guide)
8. [Policy Rules](#policy-rules)
9. [Best Practices](#best-practices)

---

## Project Structure

```
devsecops-ml-pipeline/
├── ml-service/                 # ML service application code
│   ├── app.py                 # Insecure Flask application (demo)
│   ├── inference.py           # Secure ML inference module
│   ├── requirements.txt       # Vulnerable dependencies (demo)
│   └── requirements-secure.txt # Secure dependencies
├── docker/                     # Docker configurations
│   ├── Dockerfile.insecure    # Insecure Dockerfile (demo)
│   ├── Dockerfile.secure      # Secure Dockerfile (best practice)
│   ├── docker-compose.yml     # Compose configuration
│   ├── build-insecure.sh      # Build script for insecure image
│   └── build-secure.sh        # Build script for secure image
├── ci-config/                  # CI/CD configurations
│   ├── .gitlab-ci.yml         # GitLab CI pipeline
│   └── security.yml           # GitHub Actions workflow
├── security/                   # Security policies and configurations
│   ├── trivy.yaml             # Trivy scanner configuration
│   ├── anchore-policy.yaml    # Anchore policy rules
│   └── .trivyignore           # CVE exemptions for Trivy
├── scripts/                    # Automation scripts
│   ├── scan-local.sh          # Local scanning script
│   ├── generate-report.py     # Report generation
│   └── check-dependencies.py  # Dependency checking
└── docs/                       # Documentation
    ├── README.md              # This file
    ├── SETUP.md               # Detailed setup instructions
    ├── VULNERABILITIES.md     # Known vulnerabilities reference
    └── REMEDIATION.md         # Remediation procedures
```

---

## Getting Started

### Prerequisites

- Docker and Docker Compose
- Python 3.9+
- Git
- GitLab or GitHub account (for CI/CD)

### Installation

1. **Clone and navigate to the project:**
```bash
cd devsecops-ml-pipeline
```

2. **Install security tools locally:**
```bash
# Install Trivy
curl -sfL https://raw.githubusercontent.com/aquasecurity/trivy/main/contrib/install.sh | sh -s -- -b /usr/local/bin

# Install Anchore CLI
curl -sSfL https://anchorectl.anchore.io/install.sh | sh -s -- -b /usr/local/bin

# Install Python security tools
pip install safety bandit semgrep cyclonedx-bom
```

3. **Build the Docker images:**
```bash
# Build secure image
bash docker/build-secure.sh

# Build insecure image (for demonstration)
BUILD_INSECURE=true bash docker/build-insecure.sh
```

---

## Tools Overview

### Trivy - Container and Dependency Scanner

**Purpose:** Comprehensive vulnerability scanning for containers and dependencies

**Key Features:**
- Vulnerability detection in OS packages and application libraries
- Configuration scanning (misconfigurations in Dockerfile, K8s, etc.)
- Secret detection
- Software Bill of Materials (SBOM) generation
- Fast and accurate scanning with minimal false positives

**Configuration:** [security/trivy.yaml](security/trivy.yaml)

**Resources:**
- [Trivy Documentation](https://aquasecurity.github.io/trivy/)
- [Trivy GitHub](https://github.com/aquasecurity/trivy)

### Anchore Engine - Policy-based Image Analysis

**Purpose:** Policy-driven container image analysis and compliance checking

**Key Features:**
- Detailed image analysis
- Policy enforcement
- Compliance checking
- Fine-grained control over accepted vulnerabilities
- Integration with CI/CD systems

**Configuration:** [security/anchore-policy.yaml](security/anchore-policy.yaml)

**Resources:**
- [Anchore Documentation](https://docs.anchore.com/)
- [Anchore GitHub](https://github.com/anchore/anchore-engine)

### Safety - Python Dependency Checker

**Purpose:** Checks Python packages for known security vulnerabilities

**Installation:**
```bash
pip install safety
```

**Usage:**
```bash
safety check --file requirements.txt
```

### Bandit - Python Security Issue Scanner

**Purpose:** Scans Python code for common security issues

**Installation:**
```bash
pip install bandit
```

**Usage:**
```bash
bandit -r ml-service/ -f json -o bandit-report.json
```

### Semgrep - Static Analysis

**Purpose:** Pattern-based static code analysis

**Installation:**
```bash
pip install semgrep
```

**Usage:**
```bash
semgrep --config=p/security-audit ml-service/
```

---

## Configuration Guide

### Trivy Configuration

**File:** [security/trivy.yaml](security/trivy.yaml)

**Key Configuration Options:**

```yaml
# Severity levels to report
vulnerability:
  severity:
    - CRITICAL
    - HIGH
    - MEDIUM

# Exit code on vulnerabilities found
report:
  exit-code: 1  # Non-zero exit fails the build

# Ignore specific CVEs
ignore:
  unfixed: false
```

**Customization:**

1. **Adjust severity thresholds:**
```yaml
vulnerability:
  severity:
    - CRITICAL    # Most critical
    - HIGH        # High severity only
```

2. **Set specific policy rules:**
```yaml
severity-policy:
  CRITICAL:
    max-allowed: 0
    action: fail
  HIGH:
    max-allowed: 5
    action: warn
```

3. **Skip specific CVEs** using `.trivyignore` file:
```
CVE-2021-1234 2025-12-31
CVE-2021-5678 2025-06-30
```

### Anchore Policy Configuration

**File:** [security/anchore-policy.yaml](security/anchore-policy.yaml)

**Key Policy Rules:**

1. **DOCKERFILE Gate** - Checks Dockerfile best practices:
```yaml
- id: rule-2
  gate: DOCKERFILE
  trigger: effective_user_id
  action: FAIL
  params:
    - key: user
      value: root
  description: "Image runs as root user (critical security issue)"
```

2. **VULNERABILITIES Gate** - Vulnerability enforcement:
```yaml
- id: rule-4
  gate: VULNERABILITIES
  trigger: vulnerability
  action: FAIL
  params:
    - key: severity
      value: "critical"
  description: "Critical vulnerabilities found"
```

3. **PACKAGES Gate** - Package validation:
```yaml
- id: rule-6
  gate: PACKAGES
  trigger: package_manifest_add
  action: FAIL
  params:
    - key: package_type
      value: "npm"
```

---

## Running Security Scans

### Local Scanning

#### 1. Scan with Trivy

**Image Vulnerability Scan:**
```bash
trivy image ml-service:latest
```

**Dockerfile Configuration Scan:**
```bash
trivy config docker/
```

**With Custom Configuration:**
```bash
trivy image --config security/trivy.yaml \
  --format json \
  --output trivy-report.json \
  ml-service:latest
```

**Generate SBOM:**
```bash
trivy image --format cyclonedx \
  --output sbom.json \
  ml-service:latest
```

#### 2. Scan with Anchore

**Add and analyze image:**
```bash
anchore-cli image add ml-service:latest
anchore-cli image wait ml-service:latest
```

**Policy evaluation:**
```bash
anchore-cli policy eval ml-service:latest
```

**Vulnerability report:**
```bash
anchore-cli image vuln ml-service:latest all
```

#### 3. Python Dependency Scanning

**Safety check:**
```bash
safety check --file ml-service/requirements.txt
```

**Bandit code scan:**
```bash
bandit -r ml-service/ -f json -o bandit-report.json
```

#### 4. Run All Scans (Local Script)

```bash
bash scripts/scan-local.sh
```

### GitLab CI/CD Pipeline

**Setup:**

1. **Add `.gitlab-ci.yml` to repository root:**
```bash
cp ci-config/.gitlab-ci.yml .gitlab-ci.yml
```

2. **Push to GitLab:**
```bash
git add .gitlab-ci.yml
git commit -m "Add GitLab CI/CD security pipeline"
git push origin main
```

**Pipeline Stages:**

| Stage | Purpose | Tools Used |
|-------|---------|-----------|
| analyze | Code and dependency analysis | Safety, Bandit, Semgrep |
| build | Build Docker images | Docker |
| scan | Container and config scanning | Trivy, Anchore |
| test | Runtime and functionality tests | pytest, Docker |
| deploy | Push to registry | Docker |

**View Pipeline:**
- Navigate to CI/CD → Pipelines in GitLab
- Click on pipeline to view detailed logs
- Download artifacts for reports

### GitHub Actions Workflow

**Setup:**

1. **Create workflow directory:**
```bash
mkdir -p .github/workflows
```

2. **Add workflow file:**
```bash
cp ci-config/security.yml .github/workflows/security.yml
```

3. **Push to GitHub:**
```bash
git add .github/workflows/security.yml
git commit -m "Add GitHub Actions security workflow"
git push origin main
```

**View Results:**
- Navigate to Actions tab
- Select "ML Service Security Scan Pipeline"
- View run details and security reports
- Download artifact reports

---

## CI/CD Pipeline Integration

### GitLab CI Configuration

**Key Features:**

1. **Multi-stage pipeline:**
   - Analysis stage
   - Build stage
   - Security scanning stage
   - Testing stage
   - Deployment stage

2. **Security gates:**
   - Build fails on critical vulnerabilities
   - Policy compliance checks
   - Dependency vulnerability blocking

3. **Artifact collection:**
   - Trivy reports (JSON, SARIF)
   - Anchore findings
   - SBOMs
   - Test reports

### GitHub Actions Workflow

**Key Features:**

1. **Comprehensive scanning:**
   - Trivy image scanning
   - Grype vulnerability scanning
   - OWASP dependency checking
   - Secret detection

2. **Security integration:**
   - Automatic SARIF upload to GitHub Security
   - Code scanning results visible in PRs
   - Security alerts for maintainers

3. **Build artifacts:**
   - Security reports
   - SBOMs
   - Compliance reports

---

## Remediation Guide

### Fixing Container Vulnerabilities

**1. Update Base Image:**

```dockerfile
# BEFORE (Vulnerable)
FROM ubuntu:16.04

# AFTER (Secure)
FROM ubuntu:24.04
# Or use minimal images
FROM python:3.9-slim
```

**2. Run as Non-Root User:**

```dockerfile
# Create user
RUN useradd -m appuser

# Switch to user
USER appuser
```

**3. Pin Dependency Versions:**

```dockerfile
# BEFORE (Risky)
RUN pip install flask

# AFTER (Secure)
RUN pip install flask==3.0.0
```

**4. Scan and Update Regular:**
```bash
# Check for updates weekly
trivy image ml-service:latest

# Update dependencies
pip list --outdated
```

### Fixing Python Vulnerabilities

**Vulnerable Package Example:** Flask 0.12.3

**Steps:**

1. **Identify vulnerable version:**
```bash
safety check --file requirements.txt
# Reports: CVE-2018-1000656 - Flask 0.12.3
```

2. **Update to secure version:**
```bash
pip install flask==3.0.0 --upgrade
```

3. **Update requirements file:**
```
flask==3.0.0  # Updated from 0.12.3
```

4. **Verify fix:**
```bash
safety check --file requirements.txt
# Should show no vulnerabilities
```

### Creating CVE Exemptions

**When to use:** Only when vulnerability has documented mitigation

**1. Add to `.trivyignore`:**
```
# CVE-2021-1234 2025-12-31
# Reason: Mitigated by application firewall rules
CVE-2021-5678
```

**2. Document in JIRA/Issue tracker**
**3. Set expiration date for re-evaluation**

---

## Policy Rules

### Security Policy Rules

#### Rule 1: No Critical Vulnerabilities
- **Severity:** CRITICAL
- **Action:** FAIL BUILD
- **Condition:** Any critical CVE found
- **Remediation:** Update vulnerable package to secure version

#### Rule 2: No Root User
- **Severity:** HIGH
- **Action:** FAIL BUILD
- **Condition:** Dockerfile runs as root
- **Remediation:** Create and use non-root user

#### Rule 3: Pinned Dependency Versions
- **Severity:** HIGH
- **Action:** WARN
- **Condition:** Unpinned dependencies in requirements.txt
- **Remediation:** Pin all dependencies to specific versions

#### Rule 4: No SSH Port Exposed
- **Severity:** CRITICAL
- **Action:** FAIL BUILD
- **Condition:** Port 22 exposed in Dockerfile
- **Remediation:** Remove SSH server from container

#### Rule 5: Health Checks Required
- **Severity:** MEDIUM
- **Action:** WARN
- **Condition:** No HEALTHCHECK defined
- **Remediation:** Add HEALTHCHECK instruction to Dockerfile

#### Rule 6: No Secrets in Code
- **Severity:** CRITICAL
- **Action:** FAIL BUILD
- **Condition:** Secrets/API keys detected
- **Remediation:** Use environment variables and secrets management

### Custom Policy Implementation

**Example: Enforce specific base images**

```yaml
- id: custom-rule-1
  name: "Base Image Whitelist"
  description: "Only allow specific secure base images"
  gate: DOCKERFILE
  trigger: base_image
  action: FAIL
  params:
    - key: allowed_images
      value: "python:3.9-slim,ubuntu:24.04"
```

---

## Best Practices

### 1. Container Security

✓ **Do:**
- Use specific, pinned base image versions
- Run containers as non-root user
- Define resource limits
- Include health checks
- Use minimal base images (slim, alpine)

✗ **Don't:**
- Use `latest` tag
- Run as root
- Expose unnecessary ports
- Include build tools in production image
- Use `SUDO` in containers

### 2. Dependency Management

✓ **Do:**
- Pin all dependency versions
- Regularly update dependencies
- Scan dependencies with Safety, Trivy
- Use lock files (requirements.txt)
- Audit transitive dependencies

✗ **Don't:**
- Use unpinned versions
- Ignore vulnerability warnings
- Mix old and new package versions
- Skip dependency scanning
- Use beta or pre-release versions in production

### 3. CI/CD Security

✓ **Do:**
- Fail builds on critical vulnerabilities
- Scan before merging to main branch
- Automated security gates
- Generate and track SBOMs
- Regular security scanning schedules

✗ **Don't:**
- Skip security scanning for speed
- Ignore security warnings
- Deploy unscanned images
- Disable security policies
- Hard-code credentials in CI/CD

### 4. Code Security

✓ **Do:**
- Input validation on all data
- Use parameterized queries
- Avoid eval() and exec()
- Implement proper error handling
- Use secure libraries (not pickle for untrusted data)

✗ **Don't:**
- Trust user input
- Use string concatenation for SQL
- Expose stack traces in errors
- Log sensitive data
- Use eval() on user input

### 5. Secrets Management

✓ **Do:**
- Use environment variables for secrets
- Use dedicated secrets managers
- Rotate credentials regularly
- Scan for leaked secrets
- Remove secrets from git history

✗ **Don't:**
- Hard-code secrets in code
- Commit secrets to repository
- Use weak secrets
- Log secrets
- Share secrets via email/chat

---

## Troubleshooting

### Issue: Trivy shows too many vulnerabilities

**Solution 1: Check if vulnerabilities are actually applicable**
```bash
# Review the specific CVE
trivy image --severity HIGH ml-service:latest

# Check if it affects your usage
grep <package-name> ml-service/requirements.txt
```

**Solution 2: Use severity filters**
```bash
# Only scan critical
trivy image --severity CRITICAL ml-service:latest
```

**Solution 3: Add exemptions if justified**
```bash
echo "CVE-2021-1234 2025-12-31" >> security/.trivyignore
```

### Issue: Build fails with vulnerable base image

**Solution:**
```bash
# Find alternative secure base image
# ubuntu:16.04 (EOL) → ubuntu:24.04 (LTS)
# python:2.7 (EOL) → python:3.9-slim

# Update Dockerfile
# Rebuild and rescan
trivy image ml-service:latest
```

### Issue: Anchore policy evaluation fails

**Solution:**
```bash
# Check policy syntax
anchore-cli policy validate security/anchore-policy.yaml

# Review specific rule that failed
anchore-cli image eval ml-service:latest

# Update policy rules as needed
```

---

## References

### Tools Documentation
- [Trivy Official Docs](https://aquasecurity.github.io/trivy/)
- [Anchore Engine Docs](https://docs.anchore.com/)
- [OWASP Dependency Check](https://owasp.org/www-project-dependency-check/)
- [Safety Documentation](https://pyup.io/safety/)

### Security Standards
- [NIST Container Security Guide](https://nvlpubs.nist.gov/nistpubs/SpecialPublications/NIST.SP.800-190.pdf)
- [CIS Docker Benchmark](https://www.cisecurity.org/benchmark/docker)
- [OWASP Top 10](https://owasp.org/www-project-top-ten/)

### Container Best Practices
- [Docker Security Best Practices](https://docs.docker.com/engine/security/)
- [Kubernetes Security Best Practices](https://kubernetes.io/docs/concepts/security/)
- [Azure Container Security](https://learn.microsoft.com/en-us/azure/container-instances/container-instances-image-security)

---

## Support and Questions

For issues or questions:
1. Check the troubleshooting section
2. Review tool documentation
3. Check CI/CD pipeline logs
4. Open an issue in the repository

---

**Last Updated:** January 21, 2026
**Version:** 1.0
**Maintainer:** DevSecOps Team

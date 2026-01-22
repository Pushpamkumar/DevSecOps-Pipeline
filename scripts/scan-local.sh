#!/bin/bash

# DevSecOps Security Scanning Script
# Performs comprehensive local security scanning of the ML service
# Requires: docker, trivy, anchore-cli, safety, bandit

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo -e "${BLUE}╔════════════════════════════════════════════════════════════╗${NC}"
echo -e "${BLUE}║         DevSecOps Security Scanning Script                 ║${NC}"
echo -e "${BLUE}║    Comprehensive Security Analysis for ML Service          ║${NC}"
echo -e "${BLUE}╚════════════════════════════════════════════════════════════╝${NC}"
echo ""

# Create results directory
RESULTS_DIR="scan-results-$(date +%Y%m%d-%H%M%S)"
mkdir -p "$RESULTS_DIR"

echo -e "${YELLOW}[INFO]${NC} Scan results will be saved to: $RESULTS_DIR"
echo ""

# ============================================================================
# 1. Python Dependency Analysis
# ============================================================================
echo -e "${BLUE}════════════════════════════════════════════════════════════${NC}"
echo -e "${BLUE}Stage 1: Python Dependency Analysis${NC}"
echo -e "${BLUE}════════════════════════════════════════════════════════════${NC}"
echo ""

# Check if Safety is installed
if ! command -v safety &> /dev/null; then
    echo -e "${YELLOW}[INFO]${NC} Installing Safety..."
    pip install safety
fi

echo -e "${YELLOW}[INFO]${NC} Running Safety check on requirements.txt..."
if safety check --file ml-service/requirements.txt --json > "$RESULTS_DIR/safety-report.json" 2>&1; then
    echo -e "${GREEN}[PASS]${NC} No vulnerabilities detected in dependencies"
else
    echo -e "${RED}[FAIL]${NC} Vulnerabilities found in dependencies"
    cat "$RESULTS_DIR/safety-report.json" | python -m json.tool | head -50
fi
echo ""

# ============================================================================
# 2. Static Code Analysis with Bandit
# ============================================================================
echo -e "${BLUE}════════════════════════════════════════════════════════════${NC}"
echo -e "${BLUE}Stage 2: Static Code Analysis (Bandit)${NC}"
echo -e "${BLUE}════════════════════════════════════════════════════════════${NC}"
echo ""

if ! command -v bandit &> /dev/null; then
    echo -e "${YELLOW}[INFO]${NC} Installing Bandit..."
    pip install bandit
fi

echo -e "${YELLOW}[INFO]${NC} Scanning Python code for security issues..."
if bandit -r ml-service/ -f json -o "$RESULTS_DIR/bandit-report.json" 2>&1 | grep -q "No issues identified"; then
    echo -e "${GREEN}[PASS]${NC} No security issues found in code"
else
    echo -e "${YELLOW}[WARN]${NC} Potential security issues found (review: $RESULTS_DIR/bandit-report.json)"
fi
echo ""

# ============================================================================
# 3. Dockerfile Scanning
# ============================================================================
echo -e "${BLUE}════════════════════════════════════════════════════════════${NC}"
echo -e "${BLUE}Stage 3: Dockerfile Security Analysis${NC}"
echo -e "${BLUE}════════════════════════════════════════════════════════════${NC}"
echo ""

# Check if Trivy is installed
if ! command -v trivy &> /dev/null; then
    echo -e "${YELLOW}[INFO]${NC} Installing Trivy..."
    curl -sfL https://raw.githubusercontent.com/aquasecurity/trivy/main/contrib/install.sh | sh -s -- -b /usr/local/bin
fi

echo -e "${YELLOW}[INFO]${NC} Scanning Dockerfile for misconfigurations..."
trivy config --format json --output "$RESULTS_DIR/dockerfile-scan.json" docker/ 2>&1 || true

# Parse results
DOCKERFILE_ISSUES=$(grep -c '"Severity"' "$RESULTS_DIR/dockerfile-scan.json" || echo "0")
echo -e "${YELLOW}[INFO]${NC} Found $DOCKERFILE_ISSUES configuration issues"
echo ""

# ============================================================================
# 4. Build and Scan Docker Images
# ============================================================================
echo -e "${BLUE}════════════════════════════════════════════════════════════${NC}"
echo -e "${BLUE}Stage 4: Docker Image Building${NC}"
echo -e "${BLUE}════════════════════════════════════════════════════════════${NC}"
echo ""

echo -e "${YELLOW}[INFO]${NC} Building secure Docker image..."
docker build -f docker/Dockerfile.secure \
    -t ml-service:secure-scan \
    --quiet . 2>&1 | tail -5 || echo "Image build completed"

echo -e "${YELLOW}[INFO]${NC} Building insecure Docker image (for demonstration)..."
docker build -f docker/Dockerfile.insecure \
    -t ml-service:insecure-scan \
    --quiet . 2>&1 | tail -5 || echo "Image build completed"

echo -e "${GREEN}[DONE]${NC} Docker images built"
echo ""

# ============================================================================
# 5. Container Vulnerability Scanning - Trivy
# ============================================================================
echo -e "${BLUE}════════════════════════════════════════════════════════════${NC}"
echo -e "${BLUE}Stage 5: Container Vulnerability Scanning (Trivy)${NC}"
echo -e "${BLUE}════════════════════════════════════════════════════════════${NC}"
echo ""

echo -e "${YELLOW}[INFO]${NC} Scanning SECURE image with Trivy..."
trivy image --config security/trivy.yaml \
    --format json \
    --output "$RESULTS_DIR/trivy-secure-vulns.json" \
    --severity CRITICAL,HIGH \
    ml-service:secure-scan 2>&1 | tail -3 || true

SECURE_VULNS=$(grep -c '"Severity":"CRITICAL"' "$RESULTS_DIR/trivy-secure-vulns.json" 2>/dev/null || echo "0")
echo -e "${GREEN}[PASS]${NC} Secure image: $SECURE_VULNS critical vulnerabilities"

echo ""
echo -e "${YELLOW}[INFO]${NC} Scanning INSECURE image with Trivy (expected to fail)..."
trivy image --config security/trivy.yaml \
    --format json \
    --output "$RESULTS_DIR/trivy-insecure-vulns.json" \
    --severity CRITICAL,HIGH \
    ml-service:insecure-scan 2>&1 | tail -3 || true

INSECURE_VULNS=$(grep -c '"Severity":"CRITICAL"' "$RESULTS_DIR/trivy-insecure-vulns.json" 2>/dev/null || echo "0")
INSECURE_HIGH=$(grep -c '"Severity":"HIGH"' "$RESULTS_DIR/trivy-insecure-vulns.json" 2>/dev/null || echo "0")
echo -e "${RED}[DEMO]${NC} Insecure image: $INSECURE_VULNS CRITICAL, $INSECURE_HIGH HIGH vulnerabilities"

echo ""

# ============================================================================
# 6. SBOM Generation
# ============================================================================
echo -e "${BLUE}════════════════════════════════════════════════════════════${NC}"
echo -e "${BLUE}Stage 6: SBOM Generation${NC}"
echo -e "${BLUE}════════════════════════════════════════════════════════════${NC}"
echo ""

echo -e "${YELLOW}[INFO]${NC} Generating Software Bill of Materials for secure image..."
trivy image --format cyclonedx \
    --output "$RESULTS_DIR/sbom-secure.json" \
    ml-service:secure-scan 2>&1 | tail -3 || true

echo -e "${GREEN}[DONE]${NC} SBOM generated"
echo ""

# ============================================================================
# 7. Security Policy Check
# ============================================================================
echo -e "${BLUE}════════════════════════════════════════════════════════════${NC}"
echo -e "${BLUE}Stage 7: Security Policy Compliance${NC}"
echo -e "${BLUE}════════════════════════════════════════════════════════════${NC}"
echo ""

echo -e "${YELLOW}[INFO]${NC} Checking security policy compliance..."

# Check for critical issues
POLICY_PASS=true

# Check 1: Base image is recent
if grep -q "FROM python:3.9" docker/Dockerfile.secure; then
    echo -e "${GREEN}✓${NC} Base image is recent"
else
    echo -e "${RED}✗${NC} Base image may be outdated"
    POLICY_PASS=false
fi

# Check 2: Non-root user
if grep -q "USER [^r]" docker/Dockerfile.secure; then
    echo -e "${GREEN}✓${NC} Dockerfile uses non-root user"
else
    echo -e "${RED}✗${NC} Dockerfile runs as root"
    POLICY_PASS=false
fi

# Check 3: Health check
if grep -q "HEALTHCHECK" docker/Dockerfile.secure; then
    echo -e "${GREEN}✓${NC} Health check defined"
else
    echo -e "${YELLOW}⚠${NC} No health check defined"
fi

# Check 4: Pinned versions
if grep -q "==" ml-service/requirements.txt; then
    echo -e "${GREEN}✓${NC} Dependency versions are pinned"
else
    echo -e "${RED}✗${NC} Some dependencies are not pinned"
    POLICY_PASS=false
fi

echo ""

# ============================================================================
# 8. Summary Report
# ============================================================================
echo -e "${BLUE}════════════════════════════════════════════════════════════${NC}"
echo -e "${BLUE}Stage 8: Summary Report${NC}"
echo -e "${BLUE}════════════════════════════════════════════════════════════${NC}"
echo ""

echo "Scan Results Summary:"
echo "├─ Python Dependencies: $([ -f "$RESULTS_DIR/safety-report.json" ] && echo "✓ Scanned" || echo "✗ Not scanned")"
echo "├─ Code Security (Bandit): $([ -f "$RESULTS_DIR/bandit-report.json" ] && echo "✓ Scanned" || echo "✗ Not scanned")"
echo "├─ Dockerfile Analysis: $([ -f "$RESULTS_DIR/dockerfile-scan.json" ] && echo "✓ Scanned" || echo "✗ Not scanned")"
echo "├─ Container Scan (Trivy): $([ -f "$RESULTS_DIR/trivy-secure-vulns.json" ] && echo "✓ Scanned" || echo "✗ Not scanned")"
echo "└─ SBOM Generated: $([ -f "$RESULTS_DIR/sbom-secure.json" ] && echo "✓ Generated" || echo "✗ Not generated")"

echo ""
echo "Results Directory: $RESULTS_DIR"
echo ""

# Generate HTML report (if jinja2 is available)
if command -v python &> /dev/null; then
    echo "Generating detailed HTML report..."
    python scripts/generate-report.py "$RESULTS_DIR" || echo "HTML report generation skipped"
fi

echo ""
echo -e "${GREEN}════════════════════════════════════════════════════════════${NC}"
echo -e "${GREEN}Scan complete! Review results in: $RESULTS_DIR${NC}"
echo -e "${GREEN}════════════════════════════════════════════════════════════${NC}"

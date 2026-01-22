#!/bin/bash
# Docker Security Scanning Demo - Comparing Insecure vs Secure Builds
# This script demonstrates how to use Trivy to scan Docker images for vulnerabilities

echo "========================================="
echo "Docker Security Scanning Demonstration"
echo "Comparing Insecure vs Secure Images"
echo "========================================="
echo ""

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Install Trivy if not present
if ! command -v trivy &> /dev/null; then
    echo -e "${YELLOW}Trivy not found. Installing...${NC}"
    # Installation would go here
    echo "Please install Trivy from: https://github.com/aquasecurity/trivy"
    exit 1
fi

echo -e "${BLUE}=== SCANNING INSECURE IMAGE ===${NC}"
echo "Image: ml-service:insecure"
echo "Base: ubuntu:18.04"
echo ""

# Scan insecure image
trivy image ml-service:insecure --severity HIGH,CRITICAL > /tmp/insecure-scan.txt 2>&1

echo "Vulnerabilities found (HIGH and CRITICAL):"
cat /tmp/insecure-scan.txt

echo ""
echo -e "${BLUE}=== SCANNING SECURE IMAGE ===${NC}"
echo "Image: ml-service:secure"
echo "Base: python:3.9-slim"
echo ""

# Scan secure image
trivy image ml-service:secure --severity HIGH,CRITICAL > /tmp/secure-scan.txt 2>&1

echo "Vulnerabilities found (HIGH and CRITICAL):"
cat /tmp/secure-scan.txt

echo ""
echo "========================================="
echo "Summary Comparison"
echo "========================================="

INSECURE_COUNT=$(grep -c "CVE-" /tmp/insecure-scan.txt || echo "0")
SECURE_COUNT=$(grep -c "CVE-" /tmp/secure-scan.txt || echo "0")

echo -e "Insecure Image: ${RED}$INSECURE_COUNT CVEs${NC}"
echo -e "Secure Image:   ${GREEN}$SECURE_COUNT CVEs${NC}"

echo ""
echo "Key Differences:"
echo "1. Base Image: ubuntu:18.04 (old) vs python:3.9-slim (modern)"
echo "2. Package Versioning: Unpinned vs Pinned versions"
echo "3. User Privilege: Running as root vs Non-root user"
echo "4. Image Size & Complexity: Large vs Minimal"
echo "5. SSH Enabled: Yes (CRITICAL) vs No"
echo ""

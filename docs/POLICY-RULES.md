# Policy Rules and Configuration Guide

## Overview

This document explains the security policy rules, how to configure them, and how to enforce them in your CI/CD pipeline.

## Table of Contents

1. [Trivy Policy Rules](#trivy-policy-rules)
2. [Anchore Policy Rules](#anchore-policy-rules)
3. [Custom Policy Implementation](#custom-policy-implementation)
4. [Severity Levels](#severity-levels)
5. [Policy Exceptions](#policy-exceptions)
6. [Best Practices](#best-practices)

---

## Trivy Policy Rules

### Configuration Location
- **File:** `security/trivy.yaml`
- **Format:** YAML

### Core Configuration Options

#### Scan Type Configuration

```yaml
scan:
  scanners:
    - vuln      # Vulnerability scanning (OS and application packages)
    - config    # Misconfigurations in Docker, K8s, Terraform, etc.
    - secret    # Secrets like API keys, passwords
    - license   # License compliance checking
```

#### Vulnerability Severity Levels

```yaml
vulnerability:
  severity:
    - CRITICAL  # Most severe issues (CVSS 9.0-10.0)
    - HIGH      # High severity (CVSS 7.0-8.9)
    - MEDIUM    # Medium severity (CVSS 4.0-6.9)
    - LOW       # Low severity (CVSS 0.1-3.9)
    - UNKNOWN   # Severity not yet assigned
```

#### Report Configuration

```yaml
report:
  format: json        # Output format: json, sarif, cyclonedx, table
  exit-code: 1        # Exit code when vulnerabilities found (1=fail)
  ignore-unfixed: false  # Report unfixed vulnerabilities
```

### Severity-Based Policy Example

```yaml
severity-policy:
  # Critical vulnerabilities: Fail the build
  CRITICAL:
    max-allowed: 0       # Zero tolerance
    action: fail         # Fail the build

  # High severity: Allow up to 5, warn
  HIGH:
    max-allowed: 5
    action: warn

  # Medium: Allow up to 20, just log
  MEDIUM:
    max-allowed: 20
    action: log

  # Low: Informational only
  LOW:
    max-allowed: 100
    action: log
```

### Custom Policy Rules

```yaml
policy:
  - id: "rule-001"
    name: "No Critical Vulnerabilities"
    description: "Fail build if any critical CVEs found"
    severity: CRITICAL
    action: fail

  - id: "rule-002"
    name: "Image Configuration"
    description: "Check Docker best practices"
    severity: HIGH
    action: warn

  - id: "rule-003"
    name: "Secrets Detection"
    description: "Fail if secrets found in image"
    severity: CRITICAL
    action: fail
```

### CVE Exemptions

**File:** `security/.trivyignore`

```yaml
# Format: CVE-ID YYYY-MM-DD (expiration date)

# Examples:
CVE-2021-1234 2025-12-31  # Expires in 1 year
CVE-2021-5678 2025-06-30  # Expires in 6 months

# Why exempted - Always document:
# CVE-2022-1111 2025-03-15  # Mitigated by WAF rules
# CVE-2022-2222 2025-03-15  # Fixed in 1.5.0, upgrade scheduled
```

### Usage Examples

#### Basic Scan
```bash
trivy image ml-service:latest
```

#### Scan with Custom Config
```bash
trivy image --config security/trivy.yaml \
  --format json \
  --output report.json \
  ml-service:latest
```

#### Only Show Critical/High
```bash
trivy image --severity CRITICAL,HIGH \
  ml-service:latest
```

#### Exit on Any High Vulnerability
```bash
trivy image --severity HIGH \
  --exit-code 1 \
  ml-service:latest
# Returns exit code 1 if HIGH or CRITICAL found
```

---

## Anchore Policy Rules

### Configuration Location
- **File:** `security/anchore-policy.yaml`
- **Format:** YAML

### Policy Gates

#### Gate: DOCKERFILE

Checks Dockerfile best practices:

```yaml
- id: dockerfile-1
  gate: DOCKERFILE
  trigger: exposed_port
  action: WARN
  params:
    - key: port
      value: "22"  # Warn if SSH port exposed
  description: "SSH port should not be exposed"

- id: dockerfile-2
  gate: DOCKERFILE
  trigger: effective_user_id
  action: FAIL
  params:
    - key: user
      value: root  # Fail if runs as root
  description: "Container must not run as root"

- id: dockerfile-3
  gate: DOCKERFILE
  trigger: base_image_not_known
  action: WARN
  description: "Use well-known base images only"
```

#### Gate: VULNERABILITIES

Vulnerability enforcement:

```yaml
- id: vuln-1
  gate: VULNERABILITIES
  trigger: vulnerability
  action: FAIL
  params:
    - key: severity
      value: "critical"  # Fail on critical CVEs
  description: "No critical vulnerabilities allowed"

- id: vuln-2
  gate: VULNERABILITIES
  trigger: vulnerability
  action: FAIL
  params:
    - key: severity
      value: "high"
    - key: cvssv3_score
      value: ">8.0"  # Fail on high CVSS scores
  description: "High severity CVEs with CVSS > 8.0 must be fixed"

- id: vuln-3
  gate: VULNERABILITIES
  trigger: vulnerability_age_days
  action: WARN
  params:
    - key: days
      value: "30"  # Warn if vulnerability >30 days old
  description: "Vulnerabilities should be addressed within 30 days"
```

#### Gate: PACKAGES

Package validation:

```yaml
- id: packages-1
  gate: PACKAGES
  trigger: package_manifest_add
  action: FAIL
  params:
    - key: package_type
      value: "npm"
    - key: specific_package_match
      value: "malware-package"
  description: "Malware packages not allowed"

- id: packages-2
  gate: PACKAGES
  trigger: blacklisted_name_image
  action: FAIL
  description: "Image not on blacklist"
```

#### Gate: SECRETSCANNING

Secrets detection:

```yaml
- id: secrets-1
  gate: SECRETSCANNING
  trigger: secret_found
  action: FAIL
  description: "No secrets allowed in container image"
```

#### Gate: MALWARE

Malware scanning:

```yaml
- id: malware-1
  gate: MALWARE
  trigger: malware_found
  action: FAIL
  description: "Malware signatures detected"
```

### Exception Handling

```yaml
exceptions:
  - rule_id: vuln-1
    exceptions:
      - cve_id: CVE-2021-1234
        reason: "No exploitable path in our application"
        expires: "2025-12-31"
      
      - cve_id: CVE-2021-5678
        reason: "Mitigated by network controls"
        expires: "2025-06-30"
```

### Usage Examples

#### Evaluate Policy
```bash
anchore-cli policy eval ml-service:latest
```

#### Show Policy Details
```bash
anchore-cli policy describe
```

#### Update Policy
```bash
anchore-cli policy update --policy-file security/anchore-policy.yaml
```

---

## Custom Policy Implementation

### Creating Custom Rules

#### Example 1: Enforce Specific Base Images

```yaml
- id: custom-base-image
  name: "Base Image Whitelist"
  description: "Only allow approved base images"
  gate: DOCKERFILE
  trigger: base_image
  action: FAIL
  params:
    - key: allowed_images
      value: "python:3.9-slim,ubuntu:24.04,alpine:latest"
```

#### Example 2: Python Version Check

```yaml
- id: custom-python-version
  name: "Python Version Requirement"
  description: "Enforce Python 3.9 or later"
  gate: DOCKERFILE
  trigger: FROM
  action: FAIL
  params:
    - key: regex
      value: "(python:(2\\.|3\\.[0-8]))"
    - key: not_regex
      value: "(python:(3\\.[9-9]|3\\.[1-9][0-9]))"
```

#### Example 3: Resource Limits

```yaml
- id: custom-resource-limits
  name: "Container Resource Limits"
  description: "Ensure memory and CPU limits set"
  gate: DOCKER_LABELS
  trigger: label_check
  action: WARN
  params:
    - key: required_labels
      value: "memory_limit,cpu_limit"
```

### Using Semgrep for Code Policies

**Custom Semgrep rules for ML security:**

```yaml
rules:
  - id: ml-unsafe-model-loading
    pattern: |
      pickle.load(...)
    message: "Unsafe pickle deserialization - use joblib or safetensors"
    languages: [python]
    severity: ERROR

  - id: ml-no-input-validation
    pattern: |
      @app.route(...)
      def $FUNC(...):
        ...
        data = request.get_json(...)
        ...
        # No validation
    message: "Input not validated - add validation checks"
    languages: [python]
    severity: WARNING

  - id: ml-hardcoded-secrets
    pattern-either:
      - pattern: "API_KEY = '...'"
      - pattern: "SECRET = '...'"
    message: "Hardcoded secrets detected - use environment variables"
    languages: [python]
    severity: ERROR
```

---

## Severity Levels

### CVSS Score Mapping

| CVSS Score | Severity | Recommended Action |
|-----------|----------|------------------|
| 9.0-10.0 | CRITICAL | Block immediately |
| 7.0-8.9 | HIGH | Fix within 7 days |
| 4.0-6.9 | MEDIUM | Fix within 30 days |
| 0.1-3.9 | LOW | Fix within 90 days |
| 0.0 | UNKNOWN | Investigate |

### Policy Recommendations by Severity

#### CRITICAL
```yaml
CRITICAL:
  max-allowed: 0
  action: fail
  sla_days: 1
  escalation: "P1 - Immediate"
```

#### HIGH
```yaml
HIGH:
  max-allowed: 5
  action: warn
  sla_days: 7
  escalation: "P2 - Weekly"
```

#### MEDIUM
```yaml
MEDIUM:
  max-allowed: 20
  action: log
  sla_days: 30
  escalation: "P3 - Monthly"
```

#### LOW
```yaml
LOW:
  max-allowed: 100
  action: log
  sla_days: 90
  escalation: "P4 - Quarterly"
```

---

## Policy Exceptions

### When to Create Exceptions

1. **Unfixable in timeframe:**
   - Vendor hasn't released patch
   - Breaking change required
   - Alternative vulnerable

2. **Mitigated externally:**
   - Network segmentation prevents exploit
   - Application firewall blocks attack
   - User restrictions prevent access

3. **Not applicable:**
   - Code path not used
   - Package not directly imported
   - Vulnerability requires specific conditions

### Exception Documentation

**Required information:**
```yaml
- cve_id: CVE-2021-1234
  package: flask
  version: 1.0.0
  reason: "Exploitation requires local access; app is containerized and runs in restricted environment"
  mitigation: "Network isolated, no local user access"
  expires: "2025-12-31"
  approved_by: "security-team@company.com"
  jira_ticket: "SEC-1234"
```

### Exception Expiration

- Set expiration dates: typically 6-12 months
- Review monthly: Are mitigations still valid?
- Track in issue tracker (Jira, GitHub Issues, etc.)
- Escalate if mitigations no longer valid

---

## Best Practices

### 1. Policy Design

✓ **Do:**
- Start strict, relax if needed
- Document all rules
- Review quarterly
- Version control policies
- Test policies before enforcement

✗ **Don't:**
- Have conflicting rules
- Ignore security warnings
- Blindly copy policies
- Never update policies
- Allow too many exceptions

### 2. Rule Maintenance

```yaml
# Good rule structure
- id: unique-rule-id
  name: "Human readable name"
  description: "Why this rule exists"
  severity: HIGH
  action: fail
  sla_days: 7
  documentation: "https://..."
  approved_date: "2024-01-21"
  reviewed_date: "2024-01-21"
```

### 3. Exception Management

- Maintain exception registry
- Track approval process
- Monitor exception count
- Regular review cycles
- Escalate aged exceptions

### 4. Policy Evolution

```yaml
# Example: Tightening policy over time
# Month 1: Allow 10 high vulnerabilities
# Month 2: Reduce to 5
# Month 3: Reduce to 0 (goal)

version: "1.0"  # Track policy version
effective_date: "2024-01-21"
sunset_date: "2024-03-21"  # When stricter policy takes effect
```

### 5. CI/CD Integration

```yaml
# .gitlab-ci.yml example
security_scan:
  script:
    - trivy image --exit-code 1 --severity CRITICAL,HIGH ${IMAGE}
  allow_failure: false  # Fail build on critical findings
```

### 6. Monitoring and Reporting

- Track vulnerability trends
- Monitor exception usage
- Report policy violations
- Dashboard metrics
- Monthly compliance reports

---

## Policy Templates

### Production Policy (Strictest)

```yaml
severity-policy:
  CRITICAL:
    max-allowed: 0
    action: fail
  HIGH:
    max-allowed: 0
    action: fail
  MEDIUM:
    max-allowed: 5
    action: warn
  LOW:
    max-allowed: 20
    action: log
```

### Development Policy (More Permissive)

```yaml
severity-policy:
  CRITICAL:
    max-allowed: 0
    action: fail
  HIGH:
    max-allowed: 10
    action: warn
  MEDIUM:
    max-allowed: 50
    action: log
  LOW:
    max-allowed: 100
    action: log
```

### Experimental Policy (Most Permissive)

```yaml
severity-policy:
  CRITICAL:
    max-allowed: 5
    action: warn
  HIGH:
    max-allowed: 20
    action: log
  MEDIUM:
    max-allowed: 100
    action: log
  LOW:
    max-allowed: 200
    action: log
```

---

## References

- [Trivy Documentation](https://aquasecurity.github.io/trivy/)
- [Anchore Policy Documentation](https://docs.anchore.com/current/docs/overview/concepts/policies/)
- [CVSS v3.1 Specification](https://www.first.org/cvss/v3.1/specification-document)
- [OWASP Top 10](https://owasp.org/www-project-top-ten/)

---

**Last Updated:** January 21, 2026
**Version:** 1.0

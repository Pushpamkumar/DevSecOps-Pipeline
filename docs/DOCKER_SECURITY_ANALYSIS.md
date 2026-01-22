# Docker Security Vulnerability Analysis

## Executive Summary
This document demonstrates the security differences between an intentionally insecure Docker image and a secure production-ready one.

---

## Insecure Image: ml-service:insecure

### Base Details
- **Base Image**: `ubuntu:18.04`
- **Size**: Larger (multiple megabytes)
- **Age**: Released April 2018 (6+ years old)
- **Vulnerabilities**: Many known CVEs in base OS

### Identified Security Vulnerabilities

#### 1. **Outdated Base Image** ⚠️ CRITICAL
- Ubuntu 18.04 is old and contains known vulnerabilities
- No longer receives timely security updates
- Impact: Attackers can exploit known CVEs in the OS itself

#### 2. **Root SSH Server Enabled** ⚠️ CRITICAL
```dockerfile
RUN echo "PermitRootLogin yes" >> /etc/ssh/sshd_config
```
- Exposes SSH port (22) with root login enabled
- Creates a direct attack vector for unauthorized access
- **Fix**: Remove SSH entirely or use key-based auth with non-root user

#### 3. **Running as Root User** ⚠️ CRITICAL
```dockerfile
USER root
CMD ["sh", "-c", "python3 app.py"]
```
- Container runs with full root privileges
- Any vulnerability in application = full system compromise
- **Fix**: Create non-root user and switch before running app

#### 4. **No Package Version Pinning** ⚠️ HIGH
```dockerfile
RUN apt-get update && apt-get install -y \
    python3-pip \
    curl \
    wget \
    git \
    openssh-server \
    openssh-client
```
- No version numbers specified (allows any version)
- Builds can be non-reproducible and unpredictable
- **Fix**: Pin specific versions: `curl=7.68.0-1ubuntu2`

#### 5. **Unnecessary Packages Installed** ⚠️ MEDIUM
- `openssh-server` - Not needed for app
- `curl`, `wget`, `git` - Increase attack surface
- **Fix**: Install only required packages

#### 6. **No Health Check** ⚠️ MEDIUM
- No way to verify container health
- Orchestrators can't detect failed containers
- **Fix**: Add HEALTHCHECK directive

#### 7. **Shell Form CMD** ⚠️ MEDIUM
```dockerfile
CMD ["sh", "-c", "python3 app.py"]
```
- Vulnerable to shell injection attacks
- Signal handling is incorrect
- **Fix**: Use exec form: `CMD ["python3", "app.py"]`

#### 8. **No Resource Limits** ⚠️ MEDIUM
- Container can consume unlimited CPU/memory
- Vulnerable to DoS attacks
- Implement at orchestration level

---

## Secure Image: ml-service:secure

### Base Details
- **Base Image**: `python:3.9-slim`
- **Size**: Smaller (optimized)
- **Age**: Modern, regularly updated
- **Vulnerabilities**: Minimal

### Security Best Practices Implemented

#### 1. ✅ Modern, Slim Base Image
```dockerfile
FROM python:3.9-slim as builder
```
- Based on modern Python 3.9
- "slim" variant removes unnecessary packages
- Regular security updates from Docker/Python teams
- Result: ~40% smaller, fewer vulnerabilities

#### 2. ✅ Multi-Stage Build
```dockerfile
FROM python:3.9-slim as builder
# Build dependencies (gcc, etc.) in first stage
COPY --from=builder /opt/venv /opt/venv  # Only copy result
```
- Reduces final image size by excluding build tools
- Attack surface is minimized
- Result: Only runtime dependencies included

#### 3. ✅ Non-Root User
```dockerfile
RUN groupadd -r appuser && useradd -r -g appuser appuser
USER appuser
```
- Application runs as unprivileged `appuser`
- Limits blast radius of any vulnerability
- Result: Compromised app ≠ compromised system

#### 4. ✅ No SSH Server
```dockerfile
# SSH intentionally NOT installed
```
- Removes attack vector entirely
- Container accessed via Docker exec, not SSH
- Significantly improves security posture

#### 5. ✅ Pinned Package Versions
```dockerfile
RUN pip install --upgrade pip setuptools wheel && \
    pip install -r requirements-secure.txt
```
- requirements-secure.txt has all versions pinned
- Reproducible builds across environments
- Consistent security updates

#### 6. ✅ Minimal Packages
```dockerfile
# Only curl for health checks, no unnecessary tools
RUN apt-get install -y --no-install-recommends curl
```
- Significantly smaller attack surface
- Only essentials included
- Result: ~50% fewer potential vulnerabilities

#### 7. ✅ Environment Variables
```dockerfile
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PIP_NO_CACHE_DIR=1
```
- PYTHONUNBUFFERED: Real-time logging
- PYTHONDONTWRITEBYTECODE: Prevents .pyc files
- PIP_NO_CACHE_DIR: Smaller image

#### 8. ✅ Health Check
```dockerfile
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:5000/health || exit 1
```
- Orchestrators can detect unhealthy containers
- Automatic recovery/restart possible
- Improves reliability

#### 9. ✅ Exec Form CMD
```dockerfile
ENTRYPOINT ["python"]
CMD ["app.py"]
```
- Proper signal handling (SIGTERM for graceful shutdown)
- No shell injection vulnerability
- Best practice for containerized apps

#### 10. ✅ File Ownership
```dockerfile
COPY --chown=appuser:appuser ml-service/app.py .
```
- App files owned by app user
- Prevents privilege escalation via file modification
- Correct permissions from build time

---

## Security Comparison Table

| Aspect | Insecure | Secure | Impact |
|--------|----------|--------|--------|
| Base Image | ubuntu:18.04 | python:3.9-slim | ⭐⭐⭐ |
| Root SSH | ✗ Enabled | ✓ Disabled | ⭐⭐⭐ |
| User Privilege | root | non-root | ⭐⭐⭐ |
| Package Versions | Unpinned | Pinned | ⭐⭐ |
| Image Size | ~800MB | ~300MB | ⭐⭐ |
| Installed Packages | ~20+ unnecessary | Minimal | ⭐⭐ |
| Health Check | None | ✓ Included | ⭐ |
| CMD Form | Shell (vulnerable) | Exec (safe) | ⭐ |

---

## Vulnerability Remediation Steps

### For Insecure Image:

1. **Immediate (Critical)**: 
   - [ ] Disable SSH: Remove ssh-server lines
   - [ ] Remove root access: `USER appuser`
   - [ ] Create non-root user

2. **High Priority**:
   - [ ] Update base image to python:3.9-slim or later
   - [ ] Pin package versions in requirements
   - [ ] Remove unnecessary packages (curl, wget, git, openssh-client)

3. **Medium Priority**:
   - [ ] Add HEALTHCHECK
   - [ ] Change CMD to exec form
   - [ ] Use multi-stage build

### Specific Changes:

```dockerfile
# Before (INSECURE)
FROM ubuntu:18.04
RUN apt-get install -y python3-pip curl wget git openssh-server openssh-client
RUN echo "PermitRootLogin yes" >> /etc/ssh/sshd_config
RUN pip3 install flask requests
USER root
CMD ["sh", "-c", "python3 app.py"]

# After (SECURE)
FROM python:3.9-slim
RUN apt-get update && apt-get install -y --no-install-recommends curl
RUN groupadd -r appuser && useradd -r -g appuser appuser
RUN pip install flask==2.3.3 requests==2.31.0
COPY --chown=appuser:appuser app.py .
USER appuser
HEALTHCHECK --interval=30s CMD curl -f http://localhost:5000/health || exit 1
ENTRYPOINT ["python"]
CMD ["app.py"]
```

---

## Scanning with Trivy

### Command to scan both images:

```bash
# Scan insecure image
docker run --rm -v /var/run/docker.sock:/var/run/docker.sock \
  aquasecurity/trivy image ml-service:insecure

# Scan secure image  
docker run --rm -v /var/run/docker.sock:/var/run/docker.sock \
  aquasecurity/trivy image ml-service:secure
```

### Expected Results:
- **Insecure**: 20-50+ HIGH/CRITICAL vulnerabilities
- **Secure**: 0-5 vulnerabilities (mostly in dependencies)

---

## Key Takeaways

1. **Base image matters**: Using modern, minimal base images reduces vulnerabilities by ~70%
2. **Never run as root**: Non-root users limit blast radius of compromise
3. **Pin versions**: Ensures reproducible, predictable security
4. **Minimal attack surface**: Remove unnecessary packages
5. **Monitor health**: Health checks enable automatic recovery
6. **Use proper signal handling**: Exec form CMD for graceful shutdowns

---

## References

- [Docker Security Best Practices](https://docs.docker.com/develop/security/)
- [Trivy Documentation](https://github.com/aquasecurity/trivy)
- [Dockerfile Best Practices](https://docs.docker.com/develop/dev-best-practices/)
- [CIS Docker Benchmark](https://www.cisecurity.org/cis-benchmarks/)


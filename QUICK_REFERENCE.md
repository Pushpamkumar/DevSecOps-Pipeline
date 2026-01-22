# DevSecOps ML Pipeline - Quick Reference

## 🚀 Common Commands

### Building Images
```bash
# Secure image
docker build -f docker/Dockerfile.secure -t ml-service:secure .

# Insecure image (demo)
docker build -f docker/Dockerfile.insecure -t ml-service:insecure .

# Using compose
docker-compose build
```

### Running Security Scans
```bash
# Python dependencies
safety check --file ml-service/requirements.txt

# Dockerfile
trivy config docker/

# Container image
trivy image ml-service:secure
trivy image ml-service:insecure --severity CRITICAL,HIGH

# Code analysis
bandit -r ml-service/ -f json -o bandit-report.json

# Comprehensive local scan
bash scripts/scan-local.sh
```

### CI/CD
```bash
# GitLab: Push to trigger pipeline
git add .gitlab-ci.yml
git commit -m "Add CI/CD"
git push origin main

# GitHub: Push to trigger workflow
git add .github/workflows/
git commit -m "Add workflow"
git push origin main
```

### Running Services
```bash
# Start with compose
docker-compose up -d

# Access services
# Secure:   curl http://localhost:5001/health
# Insecure: curl http://localhost:5000/health

# View logs
docker-compose logs -f ml-service-secure

# Stop services
docker-compose down
```

## 📊 Scan Results

**Expected Results:**

| Scan | Secure | Insecure |
|------|--------|----------|
| Python Deps | ✅ Pass | ❌ 10+ vulns |
| Dockerfile | ✅ Pass | ❌ 3+ issues |
| Container | ✅ 0-5 | ❌ 200+ vulns |
| Code | ✅ 0-2 | ❌ 8+ issues |
| Overall | ✅ PASS | ❌ FAIL |

## 📁 Key Files

| File | Purpose |
|------|---------|
| `docker/Dockerfile.secure` | Production Dockerfile |
| `docker/Dockerfile.insecure` | Demo vulnerable Dockerfile |
| `ml-service/requirements-secure.txt` | Safe dependencies |
| `ml-service/requirements.txt` | Vulnerable dependencies |
| `security/trivy.yaml` | Trivy configuration |
| `security/anchore-policy.yaml` | Anchore policies |
| `ci-config/.gitlab-ci.yml` | GitLab CI pipeline |
| `ci-config/security.yml` | GitHub Actions workflow |
| `scripts/scan-local.sh` | Local scanning script |

## 🔐 Security Policies

**Build Fails If:**
- ❌ CRITICAL vulnerability found
- ❌ Container runs as root
- ❌ Secrets detected in code
- ❌ Known malware signatures
- ❌ Unsafe base image

**Build Warns If:**
- ⚠️ HIGH severity vulnerabilities
- ⚠️ Outdated base image
- ⚠️ No health check defined
- ⚠️ Dependencies not pinned

**Build Passes If:**
- ✅ No critical vulnerabilities
- ✅ Non-root user configured
- ✅ Recent base image
- ✅ Versions pinned
- ✅ No secrets in code

## 📚 Documentation

- `README.md` - Quick overview
- `docs/README.md` - Complete guide
- `docs/SETUP.md` - Setup instructions
- `docs/VULNERABILITIES.md` - Vulnerability reference
- `docs/POLICY-RULES.md` - Policy configuration

## 🔧 Troubleshooting

### Docker not running
```bash
# macOS
open -a Docker

# Linux
sudo systemctl start docker

# Windows
# Open Docker Desktop
```

### Trivy database error
```bash
trivy image --download-db-only
trivy image --skip-update ml-service:latest
```

### Permission denied
```bash
# Linux
sudo usermod -aG docker $USER
newgrp docker
```

### Pipeline fails
1. Check CI/CD logs
2. Verify registry credentials
3. Review security scan output
4. Check image name format

## 📈 Performance Tips

- Use `--skip-update` flag in Trivy for faster scans
- Run scans in parallel in CI/CD
- Cache Docker layers
- Use slim base images
- Limit scan depth

## ✅ Verification Checklist

- [ ] Docker images build successfully
- [ ] Secure image passes all scans
- [ ] Insecure image shows expected vulnerabilities
- [ ] Local scans complete without errors
- [ ] CI/CD pipeline configured
- [ ] Security reports generated
- [ ] Documentation reviewed

## 🎓 Learning Path

1. Read `README.md` for overview
2. Follow `docs/SETUP.md` for setup
3. Build images and run local scans
4. Review `docs/VULNERABILITIES.md` for issues
5. Explore `docs/POLICY-RULES.md` for policies
6. Set up CI/CD pipeline
7. Customize for your needs

## 📞 Resources

- [Trivy Docs](https://aquasecurity.github.io/trivy/)
- [Anchore Docs](https://docs.anchore.com/)
- [Docker Security](https://docs.docker.com/engine/security/)
- [OWASP Top 10](https://owasp.org/www-project-top-ten/)
- [NIST Container Security](https://nvlpubs.nist.gov/nistpubs/SpecialPublications/NIST.SP.800-190.pdf)

---

**Quick Start:** `bash scripts/scan-local.sh`

**Need Help?** Check the `docs/` folder or README.md

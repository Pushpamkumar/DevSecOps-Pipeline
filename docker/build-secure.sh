#!/bin/bash
# Build secure image following best practices
# This should pass security scanning

set -e

echo "================================"
echo "Building SECURE Docker Image"
echo "================================"

cd "$(dirname "$0")"/..

# Create secure requirements file
cat > ml-service/requirements-secure.txt << 'EOF'
# ML Service Dependencies - SECURE VERSIONS
# All versions are pinned for reproducibility
# Dependencies updated to secure versions

flask==3.0.0
werkzeug==3.0.0
jinja2==3.1.2
requests==2.31.0
pyyaml==6.0
pillow==10.1.0
numpy==1.24.3
scipy==1.11.0
pandas==2.1.0
scikit-learn==1.3.0
cryptography==41.0.0

# Additional security tools
python-dotenv==1.0.0
gunicorn==21.0.0
EOF

IMAGE_NAME="ml-service:secure"
IMAGE_TAG="ml-service:secure-latest"

docker build \
    -f docker/Dockerfile.secure \
    -t "$IMAGE_NAME" \
    -t "$IMAGE_TAG" \
    --label "build.secure=true" \
    --label "build.timestamp=$(date -u +'%Y-%m-%dT%H:%M:%SZ')" \
    .

echo "Image built: $IMAGE_NAME"
echo "To scan this image, run: trivy image $IMAGE_NAME"

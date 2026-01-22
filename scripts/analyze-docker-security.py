#!/usr/bin/env python3
"""
Docker Security Comparison Script
Demonstrates vulnerabilities in insecure vs secure Docker images
"""

import json
import subprocess
import sys

class DockerAnalyzer:
    def __init__(self):
        self.insecure_image = "ml-service:insecure"
        self.secure_image = "ml-service:secure"
    
    def get_image_config(self, image_name):
        """Extract image configuration"""
        try:
            cmd = ["docker", "inspect", image_name]
            result = subprocess.run(cmd, capture_output=True, text=True)
            return json.loads(result.stdout)[0]
        except Exception as e:
            print(f"Error inspecting {image_name}: {e}")
            return None
    
    def analyze_image(self, image_name):
        """Analyze image for security issues"""
        config = self.get_image_config(image_name)
        if not config:
            return None
        
        analysis = {
            "image": image_name,
            "size_mb": config.get("Size", 0) / (1024 ** 2),
            "config": config.get("Config", {}),
            "vulnerabilities": []
        }
        
        # Check for security issues
        cmd_config = analysis["config"]
        
        # Check user
        user = cmd_config.get("User", "")
        if user == "root" or user == "":
            analysis["vulnerabilities"].append({
                "severity": "CRITICAL",
                "issue": "Running as root",
                "description": "Container runs with root privileges",
                "fix": "Create and use non-root user"
            })
        
        # Check exposed ports
        exposed_ports = cmd_config.get("ExposedPorts", {})
        if "22/tcp" in exposed_ports:
            analysis["vulnerabilities"].append({
                "severity": "CRITICAL",
                "issue": "SSH port exposed",
                "description": "Port 22 (SSH) is exposed",
                "fix": "Remove SSH server entirely"
            })
        
        # Check CMD
        cmd = cmd_config.get("Cmd", [])
        if cmd and "sh" in cmd and "-c" in cmd:
            analysis["vulnerabilities"].append({
                "severity": "HIGH",
                "issue": "Shell form CMD",
                "description": "CMD uses shell form instead of exec",
                "fix": "Use exec form: CMD [...] instead of CMD sh -c"
            })
        
        # Check healthcheck
        healthcheck = cmd_config.get("Healthcheck")
        if not healthcheck:
            analysis["vulnerabilities"].append({
                "severity": "MEDIUM",
                "issue": "No health check",
                "description": "Container has no health check defined",
                "fix": "Add HEALTHCHECK directive"
            })
        
        return analysis
    
    def print_report(self, insecure_analysis, secure_analysis):
        """Print formatted comparison report"""
        print("\n" + "="*60)
        print("DOCKER IMAGE SECURITY ANALYSIS REPORT")
        print("="*60)
        
        # Insecure Report
        print(f"\n{'INSECURE IMAGE':^60}")
        print(f"Image: {insecure_analysis['image']}")
        print(f"Size: {insecure_analysis['size_mb']:.1f} MB")
        print(f"Vulnerabilities Found: {len(insecure_analysis['vulnerabilities'])}")
        
        print("\n" + "-"*60)
        print("IDENTIFIED VULNERABILITIES:")
        print("-"*60)
        for i, vuln in enumerate(insecure_analysis['vulnerabilities'], 1):
            print(f"\n{i}. [{vuln['severity']}] {vuln['issue']}")
            print(f"   Description: {vuln['description']}")
            print(f"   Fix: {vuln['fix']}")
        
        # Secure Report
        print(f"\n\n{'SECURE IMAGE':^60}")
        print(f"Image: {secure_analysis['image']}")
        print(f"Size: {secure_analysis['size_mb']:.1f} MB")
        print(f"Vulnerabilities Found: {len(secure_analysis['vulnerabilities'])}")
        
        if secure_analysis['vulnerabilities']:
            print("\n" + "-"*60)
            print("IDENTIFIED VULNERABILITIES:")
            print("-"*60)
            for i, vuln in enumerate(secure_analysis['vulnerabilities'], 1):
                print(f"\n{i}. [{vuln['severity']}] {vuln['issue']}")
                print(f"   Description: {vuln['description']}")
                print(f"   Fix: {vuln['fix']}")
        else:
            print("\n✓ No configuration-level vulnerabilities detected!")
        
        # Comparison
        print(f"\n\n{'COMPARISON SUMMARY':^60}")
        print("="*60)
        
        insecure_critical = sum(1 for v in insecure_analysis['vulnerabilities'] 
                               if v['severity'] == 'CRITICAL')
        insecure_high = sum(1 for v in insecure_analysis['vulnerabilities'] 
                           if v['severity'] == 'HIGH')
        secure_critical = sum(1 for v in secure_analysis['vulnerabilities'] 
                             if v['severity'] == 'CRITICAL')
        secure_high = sum(1 for v in secure_analysis['vulnerabilities'] 
                         if v['severity'] == 'HIGH')
        
        print(f"\nCritical Issues:")
        print(f"  Insecure: {insecure_critical}")
        print(f"  Secure:   {secure_critical}")
        
        print(f"\nHigh Priority Issues:")
        print(f"  Insecure: {insecure_high}")
        print(f"  Secure:   {secure_high}")
        
        print(f"\nImage Size:")
        print(f"  Insecure: {insecure_analysis['size_mb']:.1f} MB")
        print(f"  Secure:   {secure_analysis['size_mb']:.1f} MB")
        size_reduction = ((insecure_analysis['size_mb'] - secure_analysis['size_mb']) 
                         / insecure_analysis['size_mb'] * 100)
        print(f"  Reduction: {size_reduction:.1f}%")
        
        print("\n" + "="*60)
        print("RECOMMENDATIONS")
        print("="*60)
        print("""
1. Always use non-root users for container processes
2. Start with minimal base images (e.g., -slim, -alpine)
3. Pin all dependency versions for reproducibility
4. Remove unnecessary packages and services
5. Implement health checks for monitoring
6. Use exec form for CMD to handle signals correctly
7. Run security scans with Trivy before deployment
8. Implement network policies and resource limits
9. Use secrets management for sensitive data
10. Regularly update base images and dependencies
        """)

def main():
    analyzer = DockerAnalyzer()
    
    print("Analyzing images...")
    insecure = analyzer.analyze_image(analyzer.insecure_image)
    secure = analyzer.analyze_image(analyzer.secure_image)
    
    if insecure and secure:
        analyzer.print_report(insecure, secure)
    else:
        print("Error: Could not analyze images. Ensure both are built.")
        sys.exit(1)

if __name__ == "__main__":
    main()

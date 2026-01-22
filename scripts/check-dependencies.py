#!/usr/bin/env python3
"""
Dependency Checker and Updater
Checks and manages Python dependencies securely
"""

import json
import subprocess
import sys
from pathlib import Path
from typing import List, Tuple

def run_command(cmd: List[str]) -> Tuple[int, str, str]:
    """Run command and return exit code, stdout, stderr"""
    result = subprocess.run(cmd, capture_output=True, text=True)
    return result.returncode, result.stdout, result.stderr

def check_dependencies() -> dict:
    """Check dependencies for vulnerabilities"""
    results = {
        "vulnerable": [],
        "outdated": [],
        "compatible": []
    }
    
    # Use pip-audit
    print("Checking dependencies with pip-audit...")
    exit_code, stdout, stderr = run_command(["pip-audit", "--format", "json"])
    
    if exit_code == 0:
        try:
            data = json.loads(stdout)
            for vuln in data.get("vulnerabilities", []):
                results["vulnerable"].append({
                    "package": vuln.get("name"),
                    "version": vuln.get("installed_version"),
                    "cve": vuln.get("id"),
                    "description": vuln.get("description")
                })
        except json.JSONDecodeError:
            print("Could not parse pip-audit output")
    
    return results

def analyze_requirements(req_file: str) -> dict:
    """Analyze requirements file"""
    analysis = {
        "total_packages": 0,
        "pinned": 0,
        "unpinned": 0,
        "prerelease": 0,
        "packages": []
    }
    
    try:
        with open(req_file, 'r') as f:
            for line in f:
                line = line.strip()
                if not line or line.startswith('#'):
                    continue
                
                analysis["total_packages"] += 1
                
                # Parse package spec
                if '==' in line:
                    pkg, version = line.split('==')
                    analysis["pinned"] += 1
                    status = "pinned"
                elif any(op in line for op in ['>=', '<=', '>', '<', '~=', '!=']):
                    analysis["unpinned"] += 1
                    pkg = line.split(any(op for op in ['>=', '<=', '>', '<', '~=', '!=']))[0]
                    status = "version-range"
                else:
                    analysis["unpinned"] += 1
                    pkg = line
                    status = "any-version"
                
                # Check for prerelease
                if 'a' in line or 'b' in line or 'rc' in line:
                    analysis["prerelease"] += 1
                
                analysis["packages"].append({
                    "name": pkg.strip(),
                    "spec": line,
                    "status": status
                })
    except FileNotFoundError:
        print(f"Requirements file not found: {req_file}")
    
    return analysis

def generate_report(analysis: dict, vulnerabilities: dict) -> None:
    """Generate analysis report"""
    print("\n" + "="*60)
    print("Dependency Analysis Report")
    print("="*60)
    
    # Vulnerability report
    if vulnerabilities["vulnerable"]:
        print(f"\n⚠️  VULNERABILITIES FOUND: {len(vulnerabilities['vulnerable'])}")
        print("-" * 60)
        for vuln in vulnerabilities["vulnerable"]:
            print(f"  Package: {vuln['package']}")
            print(f"  Version: {vuln['version']}")
            print(f"  CVE: {vuln['cve']}")
            print(f"  Issue: {vuln['description']}")
            print()
    else:
        print("\n✓ No known vulnerabilities found")
    
    # Requirements analysis
    print(f"\nRequirements Analysis:")
    print("-" * 60)
    print(f"  Total Packages: {analysis['total_packages']}")
    print(f"  Pinned Versions: {analysis['pinned']} ({analysis['pinned']/max(1, analysis['total_packages'])*100:.1f}%)")
    print(f"  Unpinned/Range: {analysis['unpinned']} ({analysis['unpinned']/max(1, analysis['total_packages'])*100:.1f}%)")
    print(f"  Prerelease: {analysis['prerelease']}")
    
    # Recommendations
    print(f"\nRecommendations:")
    print("-" * 60)
    if vulnerabilities["vulnerable"]:
        print("  1. Update vulnerable packages to fixed versions")
        print("  2. Review and update dependencies regularly")
    
    if analysis["unpinned"] > 0:
        print(f"  • Pin {analysis['unpinned']} dependencies to specific versions")
    
    if analysis["prerelease"] > 0:
        print(f"  • Avoid {analysis['prerelease']} prerelease versions in production")
    
    print()

def main():
    """Main function"""
    req_file = "ml-service/requirements.txt"
    
    if not Path(req_file).exists():
        print(f"Error: {req_file} not found")
        sys.exit(1)
    
    # Analyze requirements
    analysis = analyze_requirements(req_file)
    
    # Check for vulnerabilities
    vulnerabilities = {
        "vulnerable": [],
        "outdated": [],
        "compatible": []
    }
    
    try:
        vulnerabilities = check_dependencies()
    except Exception as e:
        print(f"Note: Could not perform vulnerability check: {e}")
    
    # Generate report
    generate_report(analysis, vulnerabilities)
    
    # Exit with error if vulnerabilities found
    if vulnerabilities["vulnerable"]:
        sys.exit(1)

if __name__ == "__main__":
    main()

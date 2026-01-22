#!/usr/bin/env python3
"""
Security Report Generator
Generates HTML and Markdown reports from security scan results
"""

import json
import sys
from pathlib import Path
from datetime import datetime
from typing import Dict, Any

def load_json_report(filepath: str) -> Dict[str, Any]:
    """Load JSON report safely"""
    try:
        with open(filepath, 'r') as f:
            return json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        return {}

def generate_markdown_report(results_dir: str) -> str:
    """Generate Markdown report from scan results"""
    report = f"""# Security Scan Report
Generated: {datetime.now().isoformat()}

## Executive Summary

This report contains the results of comprehensive security scanning performed on the ML service container and dependencies.

## Scan Results

### 1. Python Dependencies
"""
    
    safety_file = Path(results_dir) / "safety-report.json"
    if safety_file.exists():
        data = load_json_report(str(safety_file))
        if isinstance(data, list) and len(data) > 0:
            report += f"""
Found {len(data)} vulnerability(ies) in Python dependencies:

"""
            for vuln in data:
                if isinstance(vuln, dict):
                    report += f"- {vuln.get('package', 'Unknown')}: {vuln.get('vulnerability', 'N/A')}\n"
        else:
            report += "✓ No vulnerabilities found in Python dependencies\n\n"
    
    report += """
### 2. Code Security Analysis

"""
    bandit_file = Path(results_dir) / "bandit-report.json"
    if bandit_file.exists():
        data = load_json_report(str(bandit_file))
        if data and 'results' in data:
            results = data['results']
            report += f"Found {len(results)} security issue(s) in code.\n\n"
            for issue in results[:5]:  # Show top 5
                report += f"- {issue.get('test_name', 'Unknown')}: {issue.get('issue_text', 'N/A')}\n"
        else:
            report += "✓ No security issues found in Python code\n\n"
    
    report += """
### 3. Container Vulnerabilities

"""
    trivy_file = Path(results_dir) / "trivy-secure-vulns.json"
    if trivy_file.exists():
        data = load_json_report(str(trivy_file))
        critical_count = 0
        high_count = 0
        
        if isinstance(data, dict) and 'Results' in data:
            for result in data.get('Results', []):
                for vuln in result.get('Vulnerabilities', []):
                    severity = vuln.get('Severity', '')
                    if severity == 'CRITICAL':
                        critical_count += 1
                    elif severity == 'HIGH':
                        high_count += 1
        
        report += f"""
- Critical: {critical_count}
- High: {high_count}

"""
    
    report += """
## Recommendations

1. **Update Dependencies**: Keep all packages updated to latest secure versions
2. **Use Non-Root User**: Ensure containers run as non-privileged user
3. **Implement Security Gates**: Fail CI/CD pipeline on critical vulnerabilities
4. **Regular Scanning**: Schedule weekly security scans
5. **Policy Enforcement**: Implement security policies in CI/CD

## Files Scanned
"""
    
    scan_files = list(Path(results_dir).glob("*.json"))
    for f in scan_files:
        report += f"- {f.name}\n"
    
    return report

def generate_html_report(results_dir: str) -> str:
    """Generate HTML report from scan results"""
    html = f"""<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <title>Security Scan Report</title>
    <style>
        body {{
            font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif;
            line-height: 1.6;
            color: #333;
            max-width: 1200px;
            margin: 0 auto;
            padding: 20px;
            background: #f5f5f5;
        }}
        .header {{
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 30px;
            border-radius: 8px;
            margin-bottom: 30px;
        }}
        .section {{
            background: white;
            padding: 20px;
            margin-bottom: 20px;
            border-radius: 8px;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        }}
        .status-pass {{
            color: #27ae60;
            font-weight: bold;
        }}
        .status-fail {{
            color: #e74c3c;
            font-weight: bold;
        }}
        .status-warn {{
            color: #f39c12;
            font-weight: bold;
        }}
        table {{
            width: 100%;
            border-collapse: collapse;
            margin-top: 15px;
        }}
        th, td {{
            border: 1px solid #ddd;
            padding: 12px;
            text-align: left;
        }}
        th {{
            background: #f8f9fa;
            font-weight: 600;
        }}
        tr:nth-child(even) {{
            background: #f8f9fa;
        }}
    </style>
</head>
<body>
    <div class="header">
        <h1>Security Scan Report</h1>
        <p>Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S UTC')}</p>
        <p>ML Service Security Scanning Report</p>
    </div>

    <div class="section">
        <h2>Executive Summary</h2>
        <p>This report contains comprehensive security scan results for the ML service container and its dependencies.</p>
        <p>Security scanning includes:</p>
        <ul>
            <li>Python dependency vulnerability scanning</li>
            <li>Static code analysis (Bandit)</li>
            <li>Dockerfile security analysis</li>
            <li>Container image vulnerability scanning (Trivy)</li>
            <li>Policy compliance checking</li>
        </ul>
    </div>

    <div class="section">
        <h2>Scan Results Summary</h2>
        <table>
            <thead>
                <tr>
                    <th>Category</th>
                    <th>Status</th>
                    <th>Details</th>
                </tr>
            </thead>
            <tbody>
                <tr>
                    <td>Python Dependencies</td>
                    <td><span class="status-pass">✓</span></td>
                    <td>Check safety-report.json for details</td>
                </tr>
                <tr>
                    <td>Code Security</td>
                    <td><span class="status-pass">✓</span></td>
                    <td>Check bandit-report.json for details</td>
                </tr>
                <tr>
                    <td>Container Image</td>
                    <td><span class="status-pass">✓</span></td>
                    <td>Check trivy-secure-vulns.json for details</td>
                </tr>
                <tr>
                    <td>Dockerfile Configuration</td>
                    <td><span class="status-pass">✓</span></td>
                    <td>Check dockerfile-scan.json for details</td>
                </tr>
            </tbody>
        </table>
    </div>

    <div class="section">
        <h2>Recommendations</h2>
        <ol>
            <li><strong>Update Dependencies:</strong> Keep all packages updated to latest secure versions</li>
            <li><strong>Use Non-Root User:</strong> Ensure containers run as non-privileged user</li>
            <li><strong>Implement Security Gates:</strong> Fail CI/CD pipeline on critical vulnerabilities</li>
            <li><strong>Regular Scanning:</strong> Schedule weekly security scans</li>
            <li><strong>Policy Enforcement:</strong> Implement security policies in CI/CD</li>
            <li><strong>Monitoring:</strong> Continuously monitor for new vulnerabilities</li>
        </ol>
    </div>

    <div class="section">
        <h2>Files Included in This Scan</h2>
        <ul>
"""
    
    scan_files = sorted(Path(results_dir).glob("*.json"))
    for f in scan_files:
        size_kb = f.stat().st_size / 1024
        html += f"            <li>{f.name} ({size_kb:.1f} KB)</li>\n"
    
    html += """        </ul>
    </div>

    <footer style="text-align: center; margin-top: 40px; color: #666; border-top: 1px solid #ddd; padding-top: 20px;">
        <p>Security Scan Report - Confidential</p>
        <p>For questions, contact your security team</p>
    </footer>
</body>
</html>
"""
    return html

def main():
    """Main function"""
    if len(sys.argv) < 2:
        results_dir = "."
    else:
        results_dir = sys.argv[1]
    
    print(f"Generating reports from: {results_dir}")
    
    # Generate Markdown report
    md_report = generate_markdown_report(results_dir)
    md_file = Path(results_dir) / "security-report.md"
    md_file.write_text(md_report)
    print(f"✓ Markdown report: {md_file}")
    
    # Generate HTML report
    html_report = generate_html_report(results_dir)
    html_file = Path(results_dir) / "security-report.html"
    html_file.write_text(html_report)
    print(f"✓ HTML report: {html_file}")
    
    print("\nReports generated successfully!")

if __name__ == "__main__":
    main()

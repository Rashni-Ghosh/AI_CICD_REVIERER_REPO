import re


SECRET_PATTERNS = [
    r'password\s*=\s*["\'][^"\']+["\']',
    r'api[_-]?key\s*=\s*["\'][^"\']+["\']',
    r'secret\s*=\s*["\'][^"\']+["\']',
    r'token\s*=\s*["\'][^"\']+["\']',
]


DANGEROUS_PATTERNS = [
    r"subprocess\.run\s*\(.*shell\s*=\s*True",
    r"os\.system\s*\(",
    r"eval\s*\(",
    r"exec\s*\(",
]


DOCKER_PATTERNS = [
    (
        r"^FROM\s+\S+:latest",
        "Docker image uses the latest tag."
    ),
    (
        r"^\s*USER\s+root",
        "Docker container explicitly runs as root."
    ),
]

WORKFLOW_PATTERNS = [
    (
        r"Permissions:\s*(write|admin|write-all)",
        "Action permission needs to be checked. It could be too permissive."
    ),
    (
        r"uses:\s*.+@(main|master)",
        "CI/CD action references a mutable branch."
    ),
]

def run_security_checks(code: str, file_path: str):
    findings = []
    lines = code.splitlines()

    for line_number, line in enumerate(lines, start=1):
        for pattern in SECRET_PATTERNS:
            if re.search(pattern, line, re.IGNORECASE):
                findings.append(
                    {
                        "severity": "HIGH",
                        "category": "Security",
                        "file": file_path,
                        "line": line_number,
                        "issue": "Possible hard-coded secret detected.",
                        "recommendation": (
                            "Remove the secret from source code and "
                            "use environment variables or a secret manager."
                        )
                    }
                )
                break

    return findings


def run_dangerous_command_checks(code: str, file_path: str):
    findings = []
    lines = code.splitlines()

    for line_number, line in enumerate(lines, start=1):
        for pattern in DANGEROUS_PATTERNS:
            if re.search(pattern, line, re.IGNORECASE):
                findings.append(
                    {
                        "severity": "HIGH",
                        "category": "Security",
                        "file": file_path,
                        "line": line_number,
                        "issue": "Potentially dangerous command execution detected.",
                        "recommendation": (
                            "Avoid executing untrusted user input directly. "
                            "Use safer command execution patterns and validate input."
                        )
                    }
                )
                break

    return findings


def run_docker_checks(code: str, file_path: str):
    findings = []
    lines = code.splitlines()

    for line_number, line in enumerate(lines, start=1):
        for pattern, issue in DOCKER_PATTERNS:
            if re.search(pattern, line, re.IGNORECASE):
                findings.append(
                    {
                        "severity": "MEDIUM",
                        "category": "Docker",
                        "file": file_path,
                        "line": line_number,
                        "issue": issue,
                        "recommendation": (
                            "Use explicit, trusted image versions and "
                            "avoid unnecessary root privileges."
                        )
                    }
                )

    return findings

def run_workflow_checks(code: str, file_path: str):
    findings = []
    lines = code.splitlines()

    for line_number, line in enumerate(lines, start=1):
        for pattern, issue in WORKFLOW_PATTERNS:
            if re.search(pattern, line, re.IGNORECASE):
                findings.append(
                    {
                        "severity": "MEDIUM",
                        "category": "CI/CD",
                        "file": file_path,
                        "line": line_number,
                        "issue": issue,
                        "recommendation": (
                            "Pin CI/CD actions to a trusted version or "
                            "commit SHA where appropriate."
                        )
                    }
                )

    return findings
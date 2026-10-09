import requests
import json

from app.checks import (
    run_security_checks,
    run_dangerous_command_checks,
    run_docker_checks,
    run_workflow_checks
)

from app.scanner import scan_repository


OLLAMA_URL = "http://192.168.0.104:11434/api/generate"
MODEL = "qwen2.5-coder:3b"


def review_code(file_path):

    print(f"Reading file: {file_path}")

    with open(file_path, "r", encoding="utf-8") as f:
        code = f.read()

    print("File read successfully")

    # --------------------------------
    # 1. Deterministic checks
    # --------------------------------

    security_findings = run_security_checks(
        code,
        file_path
    )

    dangerous_command_findings = run_dangerous_command_checks(
        code,
        file_path
    )

    docker_findings = []

    if file_path.lower().endswith("dockerfile"):
        docker_findings = run_docker_checks(
            code,
            file_path
        )

    workflow_findings = run_workflow_checks(
        code,
        file_path
    )

    deterministic_findings = (
        security_findings
        + dangerous_command_findings
        + docker_findings
        + workflow_findings
    )

    print(
        f"Deterministic checks found "
        f"{len(deterministic_findings)} issue(s)"
    )

    # --------------------------------
    # 2. Prepare deterministic summary
    # --------------------------------

    if deterministic_findings:

        deterministic_summary = "\n".join(
            [
                (
                    f"- Line {finding['line']}: "
                    f"{finding['category']} - "
                    f"{finding['issue']}"
                )
                for finding in deterministic_findings
            ]
        )

    else:
        deterministic_summary = "No deterministic issues were found."

    # --------------------------------
    # 3. AI review
    # --------------------------------


    prompt = f"""
You are an expert senior software engineer performing an automated
code review for a CI/CD pipeline.

Your job is to identify REAL and ACTIONABLE issues in the provided source code.

Focus on issues that require understanding the code's behavior, not just
simple pattern matching.

Review the code for:

1. SECURITY
   - Unsafe handling of user input
   - Injection vulnerabilities
   - Sensitive data exposure
   - Unsafe file or command operations
   - Authentication or authorization concerns
   - Unsafe URL construction
   - SSRF or similar risks

2. RELIABILITY
   - Missing HTTP timeouts
   - Missing error handling
   - Missing HTTP status validation
   - Possible runtime failures
   - Unhandled exceptions
   - Resource handling problems

3. MAINTAINABILITY
   - Poor or confusing implementation
   - Unnecessary complexity
   - Fragile code
   - Important missing validation

IMPORTANT RULES:

- Only report issues that are actually relevant to this code.
- Do not invent vulnerabilities.
- Do not report style issues unless they have a meaningful engineering impact.
- Do not report the same issue more than once.
- Use the exact source-code line number where the issue occurs.
- Prefer specific and actionable recommendations.
- Think about how the code behaves at runtime.
- Do not explain your reasoning outside the JSON response.

The deterministic scanner has already identified the following issues: {deterministic_summary} 
IMPORTANT RULES:
- Do NOT report issues already identified at deterministic level.
- Provide specific and actionable recommendations. 
- Think about how the code behaves at runtime. 
- Do not explain your reasoning outside the JSON response.

Your MOST IMPORTANT job is to identify additional issues that require semantic understanding of the code.

Return ONLY valid JSON.

Required format:

{{
    "findings": [
        {{
            "severity": "HIGH | MEDIUM | LOW",
            "category": "Security | Reliability | Maintainability",
            "line": 1,
            "issue": "Short description of the actual problem.",
            "recommendation": "Specific recommendation to fix the problem."
        }}
    ]
}}

If there are no meaningful issues, return:

{{
    "findings": []
}}

SOURCE FILE:
{file_path}

SOURCE CODE:
{code}
"""

    print("Sending code to Ollama...")

    response = requests.post(
        OLLAMA_URL,
        json={
            "model": MODEL,
            "messages": [
                {
                    "role": "user",
                    "content": prompt
                }
            ],
            "stream": False,
            "format": "json",
            "options": {
                "temperature": 0.0, 
            }
        },
        timeout=300
    )

    response.raise_for_status()

    ai_review_text = response.json()["response"].strip()

    print("Raw Ollama response:")
    print(ai_review_text)

    # --------------------------------
    # 4. Parse AI response
    # --------------------------------

    try:

        ai_review = json.loads(ai_review_text)

    except json.JSONDecodeError:

        if ai_review_text.startswith("```json"):
            ai_review_text = ai_review_text[7:]

        if ai_review_text.endswith("```"):
            ai_review_text = ai_review_text[:-3]

        ai_review_text = ai_review_text.strip()

        try:

            ai_review = json.loads(ai_review_text)

        except json.JSONDecodeError:

            print("WARNING: Ollama returned invalid JSON")
            ai_review = {
                "findings": [],
                "error": "AI response could not be parsed as JSON",
                "raw_response": ai_review_text
            }

    print("=" * 60)
    print("PARSED AI REVIEW")
    print(ai_review)
    print("=" * 60)
    # --------------------------------
    # 5. Remove only genuine duplicates
    # --------------------------------

    filtered_ai_findings = remove_duplicate_ai_findings(
        ai_review.get("findings", []),
        deterministic_findings
    )

    ai_review["findings"] = filtered_ai_findings

    # --------------------------------
    # 6. Combined result
    # --------------------------------

    return {
        "file": file_path,
        "deterministic_findings": deterministic_findings,
        "ai_review": ai_review
    }


def remove_duplicate_ai_findings(
    ai_findings,
    deterministic_findings
):

    filtered = []

    for ai in ai_findings:

        ai_issue = ai.get("issue", "").lower().strip()
        ai_category = ai.get("category", "").lower().strip()
        ai_line = ai.get("line")

        duplicate = False

        for deterministic in deterministic_findings:

            det_issue = deterministic.get("issue", "").lower().strip()
            det_category = deterministic.get("category", "").lower().strip()
            det_line = deterministic.get("line")

            # Exact same issue
            if ai_issue == det_issue:
                duplicate = True
                break

            # Same line + same category + highly similar wording
            if (
                ai_line == det_line
                and ai_category == det_category
                and (
                    ai_issue in det_issue
                    or det_issue in ai_issue
                )
            ):
                duplicate = True
                break

        if not duplicate:
            filtered.append(ai)

    return filtered


def review_repository(repo_path):

    files = scan_repository(repo_path)

    all_results = []

    for file_path in files:

        print(f"Reviewing: {file_path}")

        result = review_code(file_path)

        all_results.append(result)

    return {
        "repository": repo_path,
        "files_reviewed": len(files),
        "results": all_results
    }

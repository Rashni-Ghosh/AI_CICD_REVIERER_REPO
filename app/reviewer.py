import requests
import json

from app.checks import (
    run_security_checks,
    run_dangerous_command_checks,
    run_docker_checks,
    run_workflow_checks
)

from app.scanner import scan_repository


OLLAMA_URL = "http://localhost:11434/api/chat"
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
Analyze this Python code.

Find ONLY these two issues:

1. HTTPS requests without an explicit timeout.
2. Bare exception handlers such as:
   except:

Do not report any other issue.

Use the exact source-code line number.

Return ONLY valid JSON in this format:

{{
    "findings": [
        {{
            "severity": "MEDIUM",
            "category": "Reliability",
            "line": 10,
            "issue": "HTTPS request does not specify a timeout.",
            "recommendation": "Specify an explicit timeout."
        }}
    ]
}}

If no issues are found, return:

{{
    "findings": []
}}

SOURCE FILE:
{file_path}

SOURCE CODE:
{code}
"""

    print("=" * 60)
    print("PROMPT SENT TO OLLAMA")
    print(prompt)
    print("=" * 60)

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
            "stream": False
        },
        timeout=120
    )

    response.raise_for_status()

    ai_review_text = response.json()["message"]["content"].strip()

    print("=" * 60)
    print("RAW OLLAMA RESPONSE")
    print(ai_review_text)
    print("=" * 60)

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

            ai_review = {
                "findings": [],
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
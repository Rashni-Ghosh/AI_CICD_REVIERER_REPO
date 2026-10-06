import json
import sys
from pathlib import Path

# Add project root to Python path
PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from app.reviewer import review_repository


# POC policy:
# MEDIUM and HIGH findings will block the CI pipeline.
BLOCKING_SEVERITIES = {"HIGH", "MEDIUM"}


def collect_findings(data):
    """
    Recursively find all finding objects in the review result.
    This works whether review_repository returns a list or dictionary.
    """

    findings = []

    if isinstance(data, dict):

        if "severity" in data and "issue" in data:
            findings.append(data)

        for value in data.values():
            findings.extend(collect_findings(value))

    elif isinstance(data, list):

        for item in data:
            findings.extend(collect_findings(item))

    return findings


def main():
    repository_path = sys.argv[1] if len(sys.argv) > 1 else "test-data"

    print("=" * 60)
    print(f"Running AI review on: {repository_path}")
    print("=" * 60)

    result = review_repository(repository_path)

    # Save complete report
    with open("ai-review-report.json", "w", encoding="utf-8") as f:
        json.dump(result, f, indent=2)

    print("\nAI review completed.")
    print("Report written to: ai-review-report.json")

    # Collect all findings
    findings = collect_findings(result)

    blocking_findings = [
        finding
        for finding in findings
        if str(finding.get("severity", "")).upper()
        in BLOCKING_SEVERITIES
    ]

    print("\n" + "=" * 60)
    print("CI REVIEW SUMMARY")
    print("=" * 60)

    print(f"Total findings: {len(findings)}")
    print(f"Blocking findings: {len(blocking_findings)}")

    if blocking_findings:

        print("\nBLOCKING FINDINGS:")

        for finding in blocking_findings:
            print(
                f"- [{finding.get('severity')}] "
                f"Line {finding.get('line')}: "
                f"{finding.get('issue')}"
            )

        print("\n❌ AI Code Review FAILED")
        print("Blocking findings must be resolved before merging.")

        return 1

    print("\n✅ AI Code Review PASSED")
    print("No blocking findings were found.")

    return 0


if __name__ == "__main__":
    sys.exit(main())
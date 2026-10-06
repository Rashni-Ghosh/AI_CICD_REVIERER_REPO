import json
import sys
from pathlib import Path

# Add project root to Python path
PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from app.reviewer import review_repository


def main():
    repository_path = sys.argv[1] if len(sys.argv) > 1 else "test-data"

    print(f"Running AI review on: {repository_path}")

    result = review_repository(repository_path)

    with open("ai-review-report.json", "w", encoding="utf-8") as f:
        json.dump(result, f, indent=2)

    print("\nAI review completed.")
    print("Report written to: ai-review-report.json")

    return 0


if __name__ == "__main__":
    sys.exit(main())